from django.db import models

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
        return self.name
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
    name=models.CharField(max_length=30,verbose_name="房间类型")
   
    bed_count=models.IntegerField(verbose_name="床位数量")
    def __str__(self):
        return self.name
    
class Room (models.Model):#房间
    room_name=models.CharField(max_length=30,verbose_name="房间名称")
    people=models.IntegerField(verbose_name="房间人数")
    room_status=models.ForeignKey(to=room_status,verbose_name="房间状态",on_delete=models.CASCADE )
    dorm=models.ForeignKey(to=dorm,verbose_name="楼栋",on_delete=models.CASCADE )
    room_type=models.ForeignKey(to=room_type,verbose_name="房间类型",on_delete=models.CASCADE ,null=True,blank=True)
    gender=models.ForeignKey(to=gender,verbose_name="性别",on_delete=models.CASCADE )
    def __str__(self):
        return self.room_name


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
    room=models.ForeignKey(to=Room,verbose_name="房间",on_delete=models.CASCADE )
    gender=models.ForeignKey(to=gender,verbose_name="性别",on_delete=models.CASCADE )
    phone=models.CharField(max_length=30,verbose_name="电话号码")
    userstatus=models.ForeignKey(to=userstatus,verbose_name="用户状态",on_delete=models.CASCADE )
    personne=models.ForeignKey(to=Personne,verbose_name="人员类型",on_delete=models.CASCADE )
    permission=models.ForeignKey(to=Permission,verbose_name="权限",on_delete=models.CASCADE )
    def __str__(self):
        return self.name
    

class occupancyrecord(models.Model):#住宿记录
    user=models.ForeignKey(to=Person,verbose_name="员工",on_delete=models.CASCADE)
    room=models.ForeignKey(to=Room,verbose_name="房间id",on_delete=models.CASCADE )
    check_in_date=models.DateField(verbose_name="入住时间")
    check_out_date=models.DateField(verbose_name="退宿时间",null=True,blank=True)
    status_choice=[('0',"正常"),('1',"退宿"),]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name='状态(0-正常,1-退宿)',default='0')
    def __str__(self):
        return self.user.name
    

class feetype(models.Model):#计费项目
    name=models.CharField(max_length=30,verbose_name="计费项目")
    fee=models.CharField(max_length=30,verbose_name="费用单价")
    bit=models.CharField(max_length=30,verbose_name="计算单位")
    status_choice=[('启用','用'),('封存','封')]
    status=models.CharField(max_length=30,verbose_name="状态",choices=status_choice)
    cdate=models.DateField(verbose_name='创建时间')
    def __str__(self):
        return self.name

class standard (models.Model):#计费标准
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间")
    feetype=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型")

class resource_useage(models.Model):#资源使用量
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间",related_name="res")
    feetype=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型")
    date=models.CharField(max_length=30,verbose_name='计算月份')
    usege=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="用量",null=True,blank=True)
    check_in_date=models.DateField(verbose_name="录入日期")
    check_people=models.CharField(max_length=30,verbose_name="录入人")

class fee_record(models.Model):#费用细则
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间",related_name="fees")
    feetype=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型")
    date=models.CharField(max_length=30,verbose_name='计算月份')
    amount=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="金额")
    status_choice=[('0',"未缴"),('1',"已缴"),("2","部分已缴")]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name='状态(0-未缴,1-已缴,2-部分已缴)',default='0')
    cdate=models.DateField(verbose_name='创建时间')
    check_people=models.CharField(max_length=30,verbose_name="录入人")
    def __str__(self):
        # 将 Decimal 转换为字符串（可加货币符号增强可读性）
        return f"{self.room}-{self.feetype.name}-{self.amount}"
    

class fee(models.Model):#费用记录
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间")
    
    total=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="总金额")
    paid=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="已缴金额")
    date=models.DateField(verbose_name='缴纳月份')
    status_choice=[("1","是"),("0","否")]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name="是否缴纳(0-是,1-否)",default=1)

class feesharing(models.Model):
    fee_record=models.ForeignKey(to=fee_record,on_delete=models.CASCADE,verbose_name="费用细则")
    fee_type=models.ForeignKey(to=feetype,on_delete=models.CASCADE,verbose_name="计费类型",default=1)
    occupancyrecord=models.ForeignKey(to=occupancyrecord,on_delete=models.CASCADE,verbose_name="住宿记录")
    feesharings=models.CharField(max_length=30,verbose_name="个人分摊金额")
    status_choice=[("1","是"),("0","否")]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name="是否缴纳(1-是)")
    start_date=models.DateField(verbose_name="开始计费日期")
    end_date=models.DateField(verbose_name="结束计费日期")
    date=models.DateField(verbose_name="缴纳时间",null=True,blank=True)

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

class a_img(models.Model):
    a_img=models.ImageField(upload_to="admin_img/",verbose_name="头像")
    is_img=models.BooleanField(default=False,verbose_name="是否启用")
    def __str__(self):
        return self.a_img.name
    
class sharing(models.Model):
    user=models.ForeignKey(occupancyrecord,on_delete=models.CASCADE,related_name="share_name")
    cold=models.DecimalField(max_digits=5,decimal_places=2,verbose_name="水费分摊费用")
    water=models.DecimalField(max_digits=5,decimal_places=2,verbose_name="水费分摊费用")
    power=models.DecimalField(max_digits=5,decimal_places=2,verbose_name="电费分摊费用")
    home=models.DecimalField(max_digits=5,decimal_places=2,verbose_name="房费分摊费用")
    amount=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="总费用分摊")
    @property
    def total(self):
        """
        实时计算总费用：空调费 + 水费 + 电费 + 房费
        无需数据库存储，调用时自动计算，确保数据一致
        """
        # 所有字段都是DecimalField，直接相加（避免浮点数精度问题）
        return self.cold + self.water + self.power + self.home

    def __str__(self):
        return f"{self.user.user.name}的费用分摊（总计：{self.total}元）"
    
class fee_record_one(models.Model):#费用细则
    room=models.ForeignKey(to=Room,on_delete=models.CASCADE,verbose_name="房间")
    cold=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="空调费")
    power=models.DecimalField(max_digits=10,decimal_places=2, max_length=30 ,verbose_name="电费")
    water=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="水费")
    home=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="房费")
    amount=models.DecimalField(max_digits=10,decimal_places=2, max_length=30,verbose_name="总金额")
    status_choice=[('0',"未缴"),('1',"已缴"),("2","部分已缴")]
    status=models.CharField(max_length=30,choices=status_choice,verbose_name='状态(0-未缴,1-已缴,2-部分已缴)',default='0')
    date=models.CharField(max_length=30,verbose_name='计算月份')
    check_people=models.CharField(max_length=30,verbose_name="录入人",default='admin')
    def __str__(self):
        # 将 Decimal 转换为字符串（可加货币符号增强可读性）
        return f"{self.room}-{self.date}-{self.amount}"
    
class discount(models.Model):
    fee_type=models.ForeignKey(feetype,on_delete=models.CASCADE,verbose_name="费用类型")
    rate=models.CharField(max_length=30,verbose_name="折扣率")

















