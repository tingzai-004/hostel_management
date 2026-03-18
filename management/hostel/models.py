from django.db import models
from django.utils import timezone
from decimal import Decimal


# Create your models here.
##区域
class area(models.Model):
    name=models.CharField(max_length=30,verbose_name="楼栋区域")

    def __str__(self):
        return self.name
    
class dorm(models.Model):#楼栋
    name=models.CharField(max_length=30,verbose_name="楼栋名称")
    area=models.ForeignKey(to=area,verbose_name="区域id",on_delete=models.CASCADE )
    def __str__(self):
        return f"{self.area.name}-{self.name}"
class Depart(models.Model):#部门属于人员管理
    depart_title=models.CharField(max_length=50,verbose_name="部门名称")
    depart_number=models.CharField(max_length=50,verbose_name="部门人数",default=6)
    def __str__(self):
        return self.depart_title
class room_status(models.Model):#房间状态宿舍资源
    
    name=models.CharField(max_length=30,verbose_name='房间状态')
    def __str__(self):
        return self.name   
    
class gender(models.Model):#性别
    name=models.CharField(max_length=30,verbose_name="性别")
    def __str__(self):
        return self.name

class room_type(models.Model):
    dorm=models.ForeignKey(to=dorm,verbose_name="区域",on_delete=models.CASCADE ,null=True,blank=True)
    name=models.CharField(max_length=30,verbose_name="房间类型")
    bed_count=models.IntegerField(verbose_name="床位数量")
    money=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="房间单价")
    cdate=models.DateField(verbose_name='创建时间', auto_now_add=True)
    status=models.BooleanField(default=True,verbose_name="是否启用")
    effective_date = models.DateField(verbose_name="生效日期", null=True, blank=True)  # 关键新增

    class Meta:
        verbose_name = "房间类型"
        verbose_name_plural = "房间类型管理"
        ordering = ['dorm', 'name', '-cdate']

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date, timedelta
        # 生效日期默认下个月1号，且不能早于下个月1号
        today = date.today()
        if not self.pk:
            if not self.effective_date:
                self.effective_date=today
            else:
                if self.effective_date<today:
                    raise ValidationError(f"生效日期必须大于今天！")
                
        else:
            if not self.effective_date:
                self.effective_date=today
            
        # 原有唯一性校验修改：只校验已生效的启用记录
        # if self.status and self.area and self.name:
        #     conflict = room_type.objects.filter(
        #         area=self.area,
        #         name=self.name,
        #         status=True,
        #         effective_date__lte=today  # 只冲突已生效的
        #     ).exclude(pk=self.pk)
        #     if conflict.exists():
        #         raise ValidationError(f"【{self.area.name}】已有启用的【{self.name}】房型（{conflict.first().money}元）")

    def save(self, *args, **kwargs):
        self.full_clean()
        from datetime import date, timedelta
        today = date.today()
        # 新记录默认生效日期为下个月1号
        if not self.pk and not self.effective_date:
            from datetime import timedelta
            self.effective_date = (today + timedelta(days=1))
        
        # 仅当新记录生效日期已到时，才停用旧记录（避免提前停用）
        if self.status and self.effective_date <=today:
            room_type.objects.filter(
                dorm=self.dorm,
                name=self.name,
                status=True,
                effective_date__lt=self.effective_date  # 只停用更早生效的
            ).exclude(pk=self.pk).update(status=False)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name}-{self.area.name}"

    
class Room (models.Model):#房间
    room_name=models.CharField(max_length=30,verbose_name="房间名称")
    people=models.IntegerField(verbose_name="房间人数",default=0)
    room_status=models.ForeignKey(to=room_status,verbose_name="房间状态",on_delete=models.CASCADE,default=1 )
    dorm=models.ForeignKey(to=dorm,verbose_name="楼栋",on_delete=models.CASCADE )
    room_type=models.ForeignKey(to=room_type,verbose_name="房间类型",on_delete=models.CASCADE ,null=True,blank=True)
    gender=models.ForeignKey(to=gender,verbose_name="性别",on_delete=models.CASCADE )
    def __str__(self):
        return f"{self.dorm}-{self.room_name}"


class userstatus(models.Model):#用户
    name=models.CharField(max_length=30,verbose_name="用户状态")
    
    def __str__(self):
        return self.name
class Personne(models.Model):#人员类型
    name=models.CharField(max_length=30,verbose_name="人员类型")
    def __str__(self):
        return self.name

class Permission(models.Model):#权限
    name=models.CharField(max_length=30,verbose_name="权限名称")
    
    def __str__(self):
        return self.name



    
class Person(models.Model):
    name=models.CharField(max_length=30,verbose_name="名字")
    password=models.CharField(max_length=128,verbose_name="初始密码")
    depart=models.ForeignKey(to=Depart,verbose_name="部门",on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,verbose_name="房间",on_delete=models.CASCADE ,null=True,blank=True)
    gender=models.ForeignKey(to=gender,verbose_name="性别",on_delete=models.CASCADE )
    phone=models.CharField(max_length=30,verbose_name="电话号码")
    userstatus=models.ForeignKey(to=userstatus,verbose_name="用户状态",on_delete=models.CASCADE )
    personne=models.ForeignKey(to=Personne,verbose_name="人员类型",on_delete=models.CASCADE )
    permission=models.ForeignKey(to=Permission,verbose_name="权限",on_delete=models.CASCADE )
    money=models.BooleanField(default=True,verbose_name="是否补贴")
    def __str__(self):
        return self.name
    

class occupancyrecord(models.Model):#住宿记录
    user=models.ForeignKey(to=Person,verbose_name="员工",on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,verbose_name="房间id",on_delete=models.CASCADE )
    check_in_date=models.DateField(verbose_name="入住时间")
    check_out_date=models.DateField(verbose_name="退宿时间",null=True,blank=True)
    discount=models.BooleanField(default=True,verbose_name="是否优惠")
    date_limit=models.CharField(max_length=30,verbose_name="优惠生效天数",default="180")
    status_choice=[('0',"正常"),('1',"退宿"),]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name='状态(0-正常,1-退宿)',default='0')

    
    def __str__(self):
        return self.user.name

from django.db import models

from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, timedelta

# 导入依赖模型

##添加费用大概是一个涨价的作用
class feetype(models.Model):#计费项目
    name=models.CharField(max_length=30,verbose_name="计费项目")
    fee=models.CharField(max_length=30,verbose_name="费用单价")
    area=models.ForeignKey(area,verbose_name="区域",on_delete=models.CASCADE)
    bit=models.CharField(max_length=30,verbose_name="计算单位")
    is_sign=models.BooleanField(default=False,verbose_name="是否固定")
    status_choice=[('启用','用'),('封存','封')]
    status=models.CharField(max_length=30,verbose_name="状态",choices=status_choice)
    cdate=models.DateField(verbose_name='创建时间')
    effective_date = models.DateField(verbose_name="生效日期", null=True, blank=True)  # 关键新增

    class Meta:
        verbose_name = "计费项目"
        verbose_name_plural = "计费项目管理"
        ordering = ['area', 'name', '-cdate']

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date, timedelta
        today = date.today()
        if not self.pk:
            if not self.effective_date:
                self.effective_date=today
            else:
                if self.effective_date<today:
                    raise ValidationError(f"生效日期必须大于等于今天！")
                
        else:
            if not self.effective_date:
                self.effective_date=today
            
        
        # 原有唯一性校验修改
        # if self.status == '启用' and self.area and self.name:
        #     conflict = feetype.objects.filter(
        #         area=self.area,
        #         name=self.name,
        #         status='启用',
        #         effective_date__lte=today
        #     ).exclude(pk=self.pk)
        #     if conflict.exists():
        #         raise ValidationError(f"【{self.area.name}】已有启用的【{self.name}】计费项目")

    def save(self, *args, **kwargs):
        self.full_clean()
        from datetime import date, timedelta
        today = date.today()
        if not self.pk and not self.effective_date:
            from datetime import timedelta
            self.effective_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        
        # 仅当生效日期已到，才封存旧记录
        if self.status == '启用' and self.effective_date <=today:
            feetype.objects.filter(
                area=self.area,
                name=self.name,
                status='启用',
                effective_date__lt=self.effective_date
            ).exclude(pk=self.pk).update(status='封存')
        super().save(*args, **kwargs)
        # if self.status =="封存" :
        #     feetype.objects.filter(
        #         area=self.area,
        #         name=self.name,
        #         status='封存',
        #         effective_date__lt=today+timedelta(days=1)
        #     ).exclude(pk=self.pk).update(status='启用')
        
            

    # class Meta:
    #     verbose_name = "计费项目"
    #     verbose_name_plural = "计费项目管理"
    #     ordering = ['area', 'name', '-cdate']  # 同区域同项目按时间倒序，最新在最前
    #     # 注意：不要加 unique_together，我们要允许多个历史版本

    # def __str__(self):
    #     fee_type = "固定费用" if self.is_fixed else "按量计费"
    #     status_text = "启用" if self.status else "停用"
    #     return f"{self.area.name} - {self.name}（{self.fee}元/{self.unit}，{fee_type}，{status_text}）"

    # # 关键：只在“启用”状态下校验同一个区域不能有重复的计费项目名
    # def clean(self):
    #     if self.status:  # 只有启用时才检查唯一性
    #         conflict = feetype.objects.filter(
    #             area=self.area,
    #             name=self.name,
    #             status=True
    #         ).exclude(pk=self.pk).first()

    #         if conflict:
    #             raise ValidationError(
    #                 f"【{self.area.name}】已经有一个启用的【{self.name}】计费项目了！\n"
    #                 f"当前启用版本：{conflict.fee}元/{conflict.unit}（创建于 {conflict.cdate.strftime('%Y-%m-%d')}）\n"
    #                 "请先停用旧版本，或者直接修改旧版本的价格。"
    #             )

    # def save(self, *args, **kwargs):
    #     self.full_clean()

    #     # 核心逻辑：只要当前这条被启用，就自动停用该区域下同名的其他所有记录
    #     if self.status:
    #         feetype.objects.filter(
    #             area=self.area,
    #             name=self.name
    #         ).exclude(pk=self.pk).update(status=False)

    #     super().save(*args, **kwargs)
    
    def __str__(self):
        fee_type = "固定费用" if self.is_sign else "用量费用"
        return f"{self.name}({fee_type})-{self.area}"

   
    """"" 
    def clean(self):
        exiting=feetype.objects.filter(
            name=self.name,
            area=self.area,
            cdate=self.cdate,
        )
        if self.id:
            exiting=exiting.exclude(id=self.id)
        if exiting.exists():
            raise ValidationError(f"该{self.name}已有记录，不可添加")
    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)  # 先保存

        # 新增或修改计费项目 → 重新计算该区域所有房间最近3个月的费用+分摊
        from .models import Room, recalculate_fee_and_sharing
        from datetime import datetime
        from dateutil.relativedelta import relativedelta  # 需要 pip install python-dateutil

        rooms = Room.objects.filter(dorm__area=self.area)
        now = datetime.now()
        months = []

        # 当月 + 前两月
        for i in range(3):
            dt = now - relativedelta(months=i)
            months.append((dt.year, dt.month))

        for room in rooms:
            for y, m in months:
                try:
                    recalculate_fee_and_sharing(room, y, m)
                except:
                    continue  # 某个月没记录就跳过

    def update_fee_record(self,is_new):
        from .models import Room, fee_record_one
        rooms = Room.objects.filter(dorm__area=self.area)
        if not rooms.exists():
            print(f"【{self.name}】该区域({self.area})暂无房间，无需更新费用")
            return
        current_year = datetime.now().year
        current_month = datetime.now().month
        months_to_calc = [(current_year, current_month)]  # 基础：当月

        if not is_new:  # 若是修改操作，追加前两个月
            for i in range(1, 3):
                target_month = current_month - i
                target_year = current_year
                # 跨年处理
                if target_month < 1:
                    target_month += 12
                    target_year -= 1
                months_to_calc.append((target_year, target_month))

        # 3. 对每个房间的指定月份重新计算费用（新增的费用类型在历史月份会自动为0）
        print(f"【{self.name}】{'新增操作，仅计算当月' if is_new else '修改操作，计算当月+前两月'}：{months_to_calc}")
        for room in rooms:
            for year, month in months_to_calc:
                print(f"更新【{room}】{year}年{month}月的{self.name}费用")
                recalculate_fee_and_sharing(room, year, month)
    
    class Meta:
        verbose_name = "计费项目"
        verbose_name_plural = "计费项目管理"
        ordering = ['-cdate', 'area', 'name']
    """"""


        
        

    
    

class standard (models.Model):#计费标准
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间")
    feetype=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型")


"""##1
# class resource_useage(models.Model):#资源使用量
#     room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间",related_name="res")
#     feetype=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型")
#     start=models.CharField(max_length=30,verbose_name='月初计数',default='89602')
#     end=models.CharField(max_length=40,verbose_name='月底计数',default='90002')
#     usege=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="用量",null=True,blank=True)
#     check_in_date=models.DateField(verbose_name="录入日期")
#     check_people=models.CharField(max_length=30,verbose_name="录入人")
#     date=models.CharField(max_length=30, verbose_name='计算月份',null=True, blank=True)"""
    
from django.core.exceptions import ValidationError   
class useage(models.Model):
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间",related_name="re")
    feetype=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型")
    start=models.CharField(max_length=30,verbose_name='月初计数',default='89602')
    end=models.CharField(max_length=40,verbose_name='月底计数',default='90002')
    usege=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="用量",null=True,blank=True)
    check_in_date=models.DateField(verbose_name="录入日期")
    check_people=models.CharField(max_length=30,verbose_name="录入人")
    def delete(self, *args, **kwargs):
        # 记住是哪个房间哪个月
        room = self.room
        year = self.check_in_date.year
        month = self.check_in_date.month
        
        # 先删除用量记录
        super().delete(*args, **kwargs)
        
        print(f"已删除用量记录：{room} {year}-{month}，重新计算费用...")
        
        # 直接调用我们最牛的函数！
        recalculate_fee_and_sharing(room, year, month)
    
    def clean(self):
        # 验证：同一房间+同一费用类型+同一月份不能重复
        existing = useage.objects.filter(
            room=self.room,
            feetype=self.feetype,
            check_in_date__year=self.check_in_date.year,
            check_in_date__month=self.check_in_date.month
        )
        if self.id:
            existing = existing.exclude(id=self.id)
        if existing.exists():
            raise ValidationError(
                f"房间{self.room}在{self.check_in_date.strftime('%Y-%m')}已存在{self.feetype.name}用量记录，不可重复添加！"
            )
    # def save(self, *args, **kwargs):
    #     # 1. 先验证 + 计算用量
    #     self.full_clean()
        
    #     try:
    #         start_val = Decimal(self.start or '0')
    #         end_val = Decimal(self.end or '0')
    #         self.usege = max(end_val - start_val, Decimal('0'))
    #     except:
    #         self.usege = Decimal('0')

    #     # 2. 保存用量记录本身
    #     super().save(*args, **kwargs)

    #     # 3. 关键：只更新费用记录，不新增！
    #     year = self.check_in_date.year
    #     month = self.check_in_date.month
    #     recalculate_fee_and_sharing(self.room, year, month)
    def save(self, *args, **kwargs):
        # 计算用量
        self.full_clean()
        try:
            start_val = Decimal(self.start or '0')
            end_val = Decimal(self.end or '0')
            self.usege = max(end_val - start_val, Decimal('0'))
        except:
            self.usege = Decimal('0')

        # 是否是新增（新增和修改都要重新算）
        is_new = self.pk is None

        # 保存用量记录
        super().save(*args, **kwargs)

        # 重点：不管新增还是修改，都强制重新计算费用 + 分摊
        from .models import recalculate_fee_and_sharing
        recalculate_fee_and_sharing(
            room=self.room,
            year=self.check_in_date.year,
            month=self.check_in_date.month
        )
'''
    # def save(self, *args, **kwargs):
    #     # 自动计算用量：月末计数 - 月初计数
    #     self.full_clean()
    #     try:
    #         # 将字符串转换为Decimal进行计算
    #         start_val = Decimal(self.start) if self.start else Decimal('0')
    #         end_val = Decimal(self.end) if self.end else Decimal('0')
    #         self.usege = end_val - start_val
    #         # 确保用量不为负数
    #         if self.usege < 0:
    #             self.usege = Decimal('0')
    #     except (ValueError, TypeError):
    #         # 处理转换错误，设置为0
    #         self.usege = Decimal('0')
        
    #     # 先保存当前用量记录
    #     super().save(*args, **kwargs)
        
    #     self.update_fee_and_sharing()

    # def update_fee_and_sharing(self):
    #     """更新费用记录和分摊，不依赖信号"""
    #     fee_date = self.check_in_date.replace(day=1)##
    #     year = self.check_in_date.year
    #     month = self.check_in_date.month
    #     room = self.room
    #     area = room.dorm.area  # 房间所属区域
    #     print("______----地区",area)

    #     # 获取或创建当月费用记录
    #     fee_record, created = fee_record_one.objects.get_or_create(
    #         room=room,
    #         # date__year=year,
    #         # date__month=month,
    #         date=fee_date,  # 直接匹配 DateField 字段的完整日期（如 2025-12-01）
    #         defaults={
    #         # 创建时强制赋值 date（即使查找失败，创建时也有值）
    #         'date': fee_date,
    #             'check_people': self.check_people,
    #             'status': '0',
    #             'amount': Decimal('0.00'),
    #             'dynamic_fees': {}
    #         }
    #     )
    #     print("___",fee_record)
    #     # 重新计算总费用
    #     total = Decimal('0.00')
    #     dynamic_fees = {}
    #     for ft in feetype.objects.filter(area=area, status='启用'):#也不一定，如果更新了那就封存了
    #         if ft.is_sign:
    #             try:
    #                 fee_amount = Decimal(ft.fee or '0')
    #                 print("___",fee_amount)
    #             except (ValueError, TypeError):
    #                 fee_amount = Decimal('0.00')
    #         else:
    #             # 用量费用：用量 × 单价
                
    #             try:
    #                 usage_obj = useage.objects.filter(
                        
    #                     room=room,
    #                     feetype=ft,
    #                     check_in_date__year=year,
    #                     check_in_date__month=month
    #                 )
    #                 if usage_obj is not None:
    #                 # 修正拼写：usege → usage（根据你的实际字段名确认！）
    #                     usage_value = Decimal(usage_obj.usage or '0')  # 防止字段值为None
    #                     price = Decimal(ft.fee or '0')
    #                     fee_amount = usage_value * price
    #                     print("价格，总额", price, fee_amount)
    #                 else:
    #                     print(f"警告：房间{room} {year}年{month}月 无{ft.name}用量记录")
    #             except (ValueError, TypeError, AttributeError) as e:
    #                 fee_amount = Decimal('0.00')
    #                 print(f"计算{ft.name}费用失败：{e}")
    #         dynamic_fees[ft.name] = float(fee_amount)
    #         print("————",dynamic_fees)
    #         total += fee_amount
    #         print("__total",total)

    #     # 更新费用记录
    #     fee_record.amount = total
    #     fee_record.dynamic_fees = dynamic_fees
    #     fee_record.save()
    #     recalculate_fee_and_sharing(room, year, month)
 '''   

   
# class fee_record(models.Model):#宿舍缴费记录
#     room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间",related_name="fees")
#     feetype=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型")
#     date=models.CharField(max_length=30,verbose_name='计算月份')
#     amount=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="金额",null=True, blank=True)
#     status_choice=[('0',"未缴"),('1',"已缴"),("2","部分已缴")]
#     status=models.CharField(max_length=30,choices=status_choice,verbose_name='状态(0-未缴,1-已缴,2-部分已缴)',default='0')
#     cdate=models.DateField(verbose_name='创建时间')
#     check_people=models.CharField(max_length=30,verbose_name="录入人")
#     def __str__(self):
#         # 将 Decimal 转换为字符串（可加货币符号增强可读性）
#         return f"{self.room}-{self.feetype.name}-{self.amount}"
    

class fee(models.Model):#费用记录
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间")
    
    total=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="总金额")
    paid=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="已缴金额")
    date=models.DateField(verbose_name='缴纳月份')
    status_choice=[("1","是"),("0","否")]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name="是否缴纳(0-是,1-否)",default=1)

# class feesharing(models.Model):
#     fee_record=models.ForeignKey(to=fee_record,on_delete=models.CASCADE,verbose_name="费用细则")
#     fee_type=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型",default=1)
#     occupancyrecord=models.ForeignKey(to=occupancyrecord,on_delete=models.CASCADE,verbose_name="住宿记录")
#     feesharings=models.CharField(max_length=30,verbose_name="个人分摊金额")
#     status_choice=[("1","是"),("0","否")]
#     status=models.CharField(max_length=30,choices=status_choice,verbose_name="是否缴纳(1-是)")
#     start_date=models.DateField(verbose_name="开始计费日期")
#     end_date=models.DateField(verbose_name="结束计费日期")
#     date=models.DateField(verbose_name="缴纳时间",null=True,blank=True)

class Admin(models.Model):
        
        password = models.CharField(max_length=128, verbose_name="初始密码")
        name = models.CharField(max_length=30, verbose_name="真实姓名", blank=True)
        email = models.EmailField(verbose_name="邮箱", blank=True)
        phone = models.CharField(max_length=30, verbose_name="联系电话", blank=True)
        depart = models.ForeignKey(Depart, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="所属部门")
        permissions = models.ForeignKey(Permission, on_delete=models.CASCADE,blank=True, verbose_name="权限")
        is_super = models.BooleanField(default=False, verbose_name="是否超级管理员")
        is_active = models.BooleanField(default=True, verbose_name="是否启用")
        create_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
        def __str__(self):
            return self.username

        class Meta:
            verbose_name = "管理员"
            verbose_name_plural = "管理员列表"
            ordering = ['-create_date']

class background(models.Model):
    name=models.CharField(max_length=30,verbose_name="上传名称")
    img=models.FileField(verbose_name="文件",max_length=128,upload_to="backgrounds/")
    is_img=models.BooleanField(default=False,verbose_name="是否激活")
    def __str__(self):
        return self.img.name

class user_img(models.Model):
    admin_img=models.ForeignKey(Admin,on_delete=models.CASCADE,related_name="avatars")
    name=models.CharField(max_length=30,verbose_name="上传名称")
    img=models.ImageField(upload_to="avatar/",verbose_name="头像")
    upload_time = models.DateTimeField(
        auto_now_add=True,  # 自动记录上传时间
        verbose_name='上传时间'
    )
    class Meta:
        ordering = ['-upload_time']  # 按上传时间倒序，最新的在最前
        verbose_name = '管理员头像'

# class a_img(models.Model):
#     a_img=models.ImageField(upload_to="admin_img/",verbose_name="头像")
#     is_img=models.BooleanField(default=False,verbose_name="是否启用")
#     def __str__(self):
#         return self.a_img.name
    
from django.db import models

    
class fee_record_one(models.Model):#费用细则
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间")
    room_fee=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="房费",null=True, blank=True)
    dynamic_fees=models.JSONField(verbose_name='动态费用项目',default=dict)
    amount=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="总金额",null=True, blank=True)
    status_choice=[('0',"未缴"),('1',"已缴"),("2","部分已缴")]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name='状态(0-未缴,1-已缴,2-部分已缴)',default='0')
    date=models.DateField(verbose_name='计算月份')
    check_people=models.CharField(max_length=30,verbose_name="录入人",default='admin')
    class Meta:
        verbose_name = "费用记录"
        verbose_name_plural = "费用记录管理"
        # 核心：同一房间+同一月份只能有一条记录
        unique_together = [['room', 'date']]
        ordering = ['-date', 'room']
    def __str__(self):
        # 将 Decimal 转换为字符串（可加货币符号增强可读性）
        return f"{self.room}-{self.date}"
    
##折扣类型添加表
class discount_feetype(models.Model):
    name=models.CharField(max_length=30,verbose_name="折扣名称")
    def __str__(self):
        return self.name
##折扣 
class discount(models.Model):
    fee_type=models.ForeignKey(discount_feetype,on_delete=models.CASCADE,verbose_name="折扣的费用类型")
    rate=models.DecimalField(max_digits=5,decimal_places=2,verbose_name="折扣率(0-1之间)")
    date=models.CharField(max_length=30,verbose_name='创建月份')
    check_in_date=models.DateField(verbose_name="生效日期",default="2025-10-01")
    # date_nums=models.CharField(max_length=30,verbose_name="生效天数",default="180")
    status=models.BooleanField(default=True,verbose_name="是否启用")

# 放在 models.py 任意位置（建议放在 sharing 模型上面）  
from decimal import Decimal
from django.db.models import F

##1



##2
class sharing(models.Model):
    user = models.ForeignKey(
        occupancyrecord, 
        on_delete=models.CASCADE, 
        verbose_name="住宿记录",
        related_name="sharing_records"
    )
    fee_record = models.ForeignKey(
        fee_record_one, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="对应的费用记录"
    )
    details = models.JSONField(default=dict, verbose_name="分摊明细")  # 关键！支持无限费用项目
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="个人总分摊")
    date = models.DateField( verbose_name="分摊生成日期")
    yuan_money=models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="院级应补贴金额")
    ketizu_money=models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="课题组应补贴金额")
    room_fee=models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="房费")

    def __str__(self):
        return f"{self.user.user.name} - {self.total}元"


##资产类别
class AssetCategory(models.Model):
    """资产类别（冰箱、空调、沙发等）"""
    name = models.CharField("资产类别", max_length=50, unique=True)

    def __str__(self):
        return self.name

##宿舍资产
class Asset(models.Model):
    """固定资产表"""
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('repairing', '维修中'),
        ('scrapped', '已报废'),
    ]

    asset_code = models.CharField("资产编号", max_length=50, unique=True)
    name = models.CharField("资产名称", max_length=100)
    category = models.ForeignKey(
        AssetCategory, on_delete=models.CASCADE, verbose_name="资产类别"
    )
    brand = models.CharField("品牌", max_length=100, blank=True)
    model = models.CharField("型号", max_length=100, blank=True)
    purchase_date = models.DateField(verbose_name="购买日期")
    price = models.DecimalField("购买价格", max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='normal')
    
    # 关键：绑定到哪个宿舍（一个资产只能属于一个宿舍）
    room = models.ForeignKey(
        Room, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="所属宿舍", related_name="assets"
    )
    bound_at = models.DateTimeField("绑定时间", auto_now_add=True)##自动生成时间，但只能生成一次，不会改变，什么时候创建就生成什么时间


    def __str__(self):
        return f"{self.asset_code} - {self.name}"
    

    
# ========== 费用+分摊计算核心函数（粘贴到models.py末尾） ==========
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.utils import timezone
from .models import (
    fee_record_one, useage, occupancyrecord, 
    sharing, room_type, Person
)

def recalculate_fee_and_sharing(room, year: int, month: int):
    """
    计算指定房间在指定年月的费用，使用该年月有效的价格（新增生效日期逻辑）
    """
    from decimal import Decimal, ROUND_HALF_UP
    from datetime import datetime, date

    # 1. 校验年月并生成当月最后一天（用于判断价格是否在当月生效）
    try:
        # 计算月份的第一天（用于费用记录）
        fee_date = date(year, month, 1)
        # 计算月份的最后一天（用于判断价格是否在当月生效）
        if month == 12:
            last_day = date(year+1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year , month + 1, 1) - timedelta(days=1)
    except (ValueError, TypeError):
        print(f"无效的年月：{year}年{month}月，跳过计算")
        return

    # 2. 获取或创建费用记录
    fee_record, created = fee_record_one.objects.get_or_create(
        room=room,
        date=fee_date,
        defaults={
            'check_people': 'system',
            'status': '0',
            'amount': Decimal('0.00'),
            'dynamic_fees': {},
            'room_fee': Decimal('0.00')
        }
    )

    # 3. 计算房费（使用计算月份有效的room_type价格）
    total_amount = Decimal('0.00')
    dynamic_fees = {}
    room_fee = Decimal('0.00')

    # 核心：获取计算月份有效的房间类型（生效日期≤当月最后一天，且状态启用）
    dorm = getattr(room, 'dorm', None)
    valid_room_type = room_type.objects.filter(  
        dorm=dorm,
        status=True,
        effective_date__lte=last_day  # 关键：只取当月已生效的价格
    ).order_by('-effective_date').first()  # 取最新生效的

    if valid_room_type and valid_room_type.money is not None:
        try:
            room_fee = Decimal(str(valid_room_type.money)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        except (ValueError, TypeError):
            room_fee = Decimal('0.00')
            print(f"房间类型 {valid_room_type.name} 金额格式错误，房费设为0")
    else:
        print(f"房间 {room} 在 {year}年{month}月 无有效房间类型，房费设为0")

    # 4. 计算用量费用（使用计算月份有效的feetype价格）
    usage_records = useage.objects.filter(
        room=room,
        check_in_date__year=year,
        check_in_date__month=month
    ).select_related('feetype')
    
    for usage in usage_records:
        ft = usage.feetype
        # 筛选计算月份有效的计费项目（生效日期≤当月最后一天，且状态启用）
        if ft.status != '启用' or (ft.area and ft.area != area):
            continue
        # 关键：判断该计费项目在计算月份是否已生效
        if ft.effective_date > last_day:
            print(f"{ft.name} 在 {year}年{month}月 未生效（生效日期：{ft.effective_date}），跳过")
            continue

        try:
            price = Decimal(str(ft.fee).strip()) if ft.fee  else Decimal('0.00')
            usage_value = usage.usege or Decimal('0.00')
            amount = (usage_value * price).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        except (ValueError, TypeError):
            amount = Decimal('0.00')
            print(f"计算 {ft.name} 费用失败")

        dynamic_fees[ft.name] = float(amount)
        total_amount += amount

    # 5. 更新费用记录
    fee_record.room_fee = room_fee
    fee_record.amount = (room_fee + total_amount).quantize(Decimal('0.00'))
    fee_record.dynamic_fees = dynamic_fees
    fee_record.save()

    # 6. 触发分摊计算
    calculate_sharing_simple(fee_record, year, month)

    print(f"{room} {year}年{month}月 费用计算完成（房费：{room_fee}，总费用：{fee_record.amount}")



def calculate_sharing_simple(fee_record, year: int, month: int):
    """
    超级分摊函数 v5.0 - 完整业务逻辑！
    1. 核心规则：入住≤180天+discount=True 才享受补贴，否则全额承担
    2. 学生（满足补贴条件）：房费实收100元，差额由院级/课题组各承担50%
    3. 员工（满足补贴条件）：房费平摊后实收50%，剩余50%由院级/课题组各承担25%
    4. 不满足补贴条件：学生/员工全额承担房费，无补贴
    5. 修复date字段为空问题，补充完整异常处理
    """
    from decimal import Decimal, ROUND_HALF_UP
    from django.utils import timezone
    from datetime import date, timedelta
    from .models import occupancyrecord, sharing, Person

    print(f"\n===== 开始计算分摊 ======")
    print(f"房间：{fee_record.room}，月份：{year}年{month}月，费用记录ID：{fee_record.id}")

    # 1. 校验总金额，避免无效计算
    total_amount = fee_record.amount or Decimal('0.00')
    if total_amount <= Decimal('0.00'):
        print("总金额为0，跳过分摊计算")
        return [], 0.0, 0.0

    # 2. 筛选有效在住人员
    occupants = occupancyrecord.objects.filter(
        room=fee_record.room,
        check_in_date__lte=fee_record.date,
        status='0',  # 0=在住
        check_out_date__isnull=True  # 未退房（无该字段可删除）
    ).select_related('user')

    if not occupants.exists():
        print(f"房间 {fee_record.room} {year}年{month}月 无有效在住人员")
        return [], 0.0, 0.0

    occupant_count = len(occupants)
    print(f"有效在住人数：{occupant_count}人")

    # 3. 仅删除当前费用记录的旧分摊（保留历史）
    sharing.objects.filter(fee_record=fee_record).delete()

    # 4. 核心：读取总房费，初始化补贴
    total_room_fee = Decimal(str(fee_record.room_fee or '0.00')).quantize(Decimal('0.00'))
    print(f"总房费（固定字段）：{total_room_fee}元")
    subsidy_a = Decimal('0.00')  # 院级补贴总计
    subsidy_b = Decimal('0.00')  # 课题组补贴总计
    # fee_type=discount.objects.filter(fee_type="房费")

    # 5. 遍历人员计算分摊（核心逻辑+180天补贴判断）
    for occupant in occupants:
        try:
            person = occupant.user
            if not person:
                print(f"在住记录 {occupant.id} 无关联用户，跳过")
                continue

            # 初始化个人数据
            detail = {}
            personal_total = Decimal('0.00')
            personal_room_fee = Decimal('0.00')
            person_subsidy_a = Decimal('0.00')  # 该人员院级补贴
            person_subsidy_b = Decimal('0.00')  # 该人员课题组补贴

            # ====== 关键：判断是否享受180天补贴资格 ======
            can_get_subsidy = False
            effective_date=occupant.date_limit
            if hasattr(occupant, 'discount') and occupant.discount:  # 住宿记录标记可优惠
                # 计算入住天数（当前日期 - 入住日期）
                check_in_date = occupant.check_in_date
                days_in = (timezone.now().date() - check_in_date).days
                if days_in <= effective_date:  # 180天有效期内
                    can_get_subsidy = True
                    print(f"{person.name} 入住{days_in}天 ≤180天，且标记优惠 → 享受补贴")
                else:
                    print(f"{person.name} 入住{days_in}天 >180天 → 不享受补贴，全额承担房费")
            else:
                print(f"{person.name} 住宿记录未标记优惠 → 不享受补贴，全额承担房费")
            
            # ====== 1. 房费分摊逻辑（区分补贴/无补贴） ======
            # 判断人员类型
            try:
                person_type = person.personne.name if hasattr(person, 'personne') else "员工"
            except Exception as e:
                person_type = "员工"
                print(f"{person.name} 人员类型获取失败，默认按员工处理：{e}")
            
            if person_type == "学生":
                if can_get_subsidy:
                    # 学生+补贴资格：实收100元，差额补贴
                    personal_room_fee = Decimal('100.00')
                    # 计算该学生对应的人均差额补贴
                    total_actual_room_fee = personal_room_fee * occupant_count
                    total_subsidy_needed = total_room_fee - total_actual_room_fee
                    if total_subsidy_needed > 0:
                        per_person_subsidy = (total_subsidy_needed / occupant_count).quantize(Decimal('0.00'))
                        person_subsidy_a = per_person_subsidy / 2
                        person_subsidy_b = per_person_subsidy / 2
                else:
                    # 学生+无补贴资格：全额平摊房费
                    personal_room_fee = Decimal('100.00')
                print(f"{person.name}(学生)：房费实收{personal_room_fee:.2f}元")

            else:  # 员工
                # 先计算平摊基础房费
                rate=discount.objects.get(fee_type="房费").rate
                normal_share = (total_room_fee / occupant_count).quantize(Decimal('0.00'))
                if can_get_subsidy:
                    # 员工+补贴资格：实收50%，剩余50%补贴
                    personal_room_fee = (normal_share * Decimal('rate')).quantize(Decimal('0.00'))
                    # 该员工对应的补贴：平摊额的25%（院级）+25%（课题组）
                    person_subsidy_a = (normal_share * Decimal('0.25')).quantize(Decimal('0.00'))
                    person_subsidy_b = (normal_share * Decimal('0.25')).quantize(Decimal('0.00'))
                else:
                    # 员工+无补贴资格：全额承担平摊房费
                    personal_room_fee = normal_share
                print(f"{person.name}(员工)：房费实收{personal_room_fee:.2f}元（原价{normal_share:.2f}）")

            # 累计补贴到总计
            subsidy_a += person_subsidy_a
            subsidy_b += person_subsidy_b

            # 房费计入个人总额
            personal_total += personal_room_fee

            # ====== 2. 其他动态费用（水电等）平摊（无补贴） ======
            for fee_name, amount in fee_record.dynamic_fees.items():
                if not amount:
                    continue
                fee_amt = Decimal(str(amount)).quantize(Decimal('0.00'))
                per_amt = (fee_amt / occupant_count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                detail[fee_name] = float(per_amt)
                personal_total += per_amt
                print(f"  {fee_name}：人均{per_amt:.2f}元")

            # ====== 3. 保存分摊记录（修复date字段） ======
            # 兼容DateField/CharField类型
            if isinstance(fee_record.date, date):
                share_date = fee_record.date
            else:
                share_date = date(year, month, 1)  # 或转字符串：str(year)+"-"+str(month).zfill(2)

            sharing.objects.create(
                user=occupant,
                fee_record=fee_record,
                room_fee=float(personal_room_fee),
                details=detail,
                total=float(personal_total.quantize(Decimal('0.00'))),
                yuan_money=float(person_subsidy_a),  # 该人员院级补贴
                ketizu_money=float(person_subsidy_b),  # 该人员课题组补贴
                date=share_date,  # 修复date字段为空
            )

            print(f"{person.name} 分摊完成，总计：{personal_total:.2f}元（房费{personal_room_fee:.2f} + 其他{personal_total-personal_room_fee:.2f}）")
            print(f"  → 院级补贴：{person_subsidy_a:.2f}元，课题组补贴：{person_subsidy_b:.2f}元")

        except Exception as e:
            print(f"处理 {person.name if 'person' in locals() else '未知用户'} 分摊出错：{e}")
            import traceback
            traceback.print_exc()
            continue

    # 6. 最终统计
    subsidy_a_total = subsidy_a.quantize(Decimal('0.00'))
    subsidy_b_total = subsidy_b.quantize(Decimal('0.00'))
    print(f"\n===== 分摊计算完成 ======")
    print(f"房间 {fee_record.room} 总院级补贴：{subsidy_a_total:.2f}元")
    print(f"房间 {fee_record.room} 总课题组补贴：{subsidy_b_total:.2f}元")
    
    return [], float(subsidy_a_total), float(subsidy_b_total)


def calculate_sharing_simple1(fee_record, year: int, month: int):
    """全新分摊函数：根据住宿记录的 discount 字段 + 180天有效期决定是否打折"""
    
    # 强制加这三行！放在函数最前面！
    from decimal import Decimal, ROUND_HALF_UP
    from django.utils import timezone
    from datetime import date
    
    # 原来的 from .models import ... 可以保留，也可以删，反正下面这行必须有
    from .models import occupancyrecord, sharing, Person, feetype,discount
    
    print("开始计算分摊：", fee_record.room, fee_record.date)
    if fee_record.amount <= Decimal('0.00'):
        print("总金额为0，跳过分摊")
        return

    # 1. 找出这个房间、当月、在住（status='0'）的所有住宿记录
    occupants = occupancyrecord.objects.filter(
        room=fee_record.room,
        check_in_date__lte=fee_record.date,   # 入住时间 ≤ 本月
        status='0'  # 正常在住
    )
    if not occupants.exists():
        print("无在住人员，跳过分摊")
        return

    # 2. 删除旧的分摊记录
    sharing.objects.filter(fee_record=fee_record).delete()

    # 3. 遍历每个人，单独算他该不该打折
    for occupant in occupants:
        try:
            person = occupant.user  # Person 对象

            detail = {}
            total = Decimal('0.00')

            # 关键：这个人是否享受优惠？满足两个条件才打折
            can_discount = False

            if occupant.discount:  # 住宿记录里写了“是否优惠”
                # 计算从入住日到今天过了多少天
                days_in = (timezone.now().date() - occupant.check_in_date).days
                if days_in <= 180:  # 没超过180天
                    can_discount = True
                    print(f"{person.name} 在住{days_in}天 ≤180天，且有优惠资格 → 打折！")
                else:
                    print(f"{person.name} 在住{days_in}天 >180天 → 不打折")
            else:
                print(f"{person.name} 住宿记录未勾选优惠 → 不打折")

            # 4. 遍历本月所有费用项目
            for fee_name, fee_amount in fee_record.dynamic_fees.items():
                if not fee_amount:
                    continue

                discounted_amt = discount.objects.filter(
                    fee_type__name=fee_name,
                    status=True,
                ).first()

                per_amt = Decimal(str(fee_amount)) / len(occupants)
                per_amt = per_amt.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

                # 只有“房费”才能打折，其他费用一律不打
                if fee_name == "房费" and can_discount:
                    # 打8折（您可以改成其他折扣）
                    per_amt = (per_amt * Decimal(discounted_amt.rate)).quantize(Decimal('0.00'))
                    print(f"  → {fee_name} 折扣：{per_amt}")

                detail[fee_name] = float(per_amt)
                total += per_amt

            # 5. 保存分摊记录
            sharing.objects.create(
                user=occupant,
                fee_record=fee_record,
                details=detail,
                total=float(total)
            )
            print(f"{person.name} 分摊完成，总计：{total}元")

        except Exception as e:
            print(f"分摊出错：{person.name} - {e}")
            continue

    print("本房间分摊全部完成！")
def calculate_sharing(fee_record, year: int, month: int):
    """极简版分摊计算"""
    from .models import occupancyrecord, sharing, Person, feetype, discount
    from decimal import Decimal, ROUND_HALF_UP
    from django.db.models import Q

    # 总金额为0/无在住人员，直接返回
    print("___调用成功")
    if fee_record.amount <= Decimal('0.00'):
        return
    occupants = occupancyrecord.objects.filter(
        room=fee_record.room,
        check_in_date__lte=fee_record.date,
        status='0',
    )
    if not occupants.exists():
        return

    # 获取房费折扣
    
    discount_rate = Decimal('1.00')
    try:
        room_fee = feetype.objects.get(name="房费", area=fee_record.room.dorm.area, status='启用')
        discount_obj = discount.objects.get(fee_type=room_fee, date=f"{year}-{month:02d}")
        discount_rate = Decimal(discount_obj.rate) / 100
    except:
        pass

    # 删除旧分摊+计算新分摊
    sharing.objects.filter(fee_record=fee_record).delete()
    occupant_count = occupants.count()

    for occupant in occupants:
        try:
            person = Person.objects.get(id=occupant.user_id)
            detail = {}
            total = Decimal('0.00')

            for name, amt in fee_record.dynamic_fees.items():
                per_amt = (Decimal(str(amt)) / occupant_count).quantize(Decimal('0.00'))
                # 房费折扣
                if name == "房费" and person.money:
                    per_amt = (per_amt * discount_rate).quantize(Decimal('0.00'))
                detail[name] = float(per_amt)
                total += per_amt

            sharing.objects.get_or_create(user=occupant, fee_record=fee_record, details=detail, total=float(total))
        except:
            continue

class money_upload(models.Model):
    name=models.CharField(max_length=30,verbose_name="上传者姓名-房间号-楼栋号")
    img=models.FileField(verbose_name="文件",max_length=128,upload_to="money_upload/")
    is_img=models.BooleanField(default=False,verbose_name="是否激活")
    def __str__(self):
        return self.img.name















