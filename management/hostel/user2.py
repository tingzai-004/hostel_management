from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
from hostel.bootstrap import BootStrapForm
import logging
from django.core.paginator import Paginator
import hashlib
from decimal import Decimal,DivisionByZero
from django.db.models import Count,Sum


logger=logging.getLogger('management')
def md5(data_string):
    if data_string is None:
        # 可以选择返回一个默认值，或者抛出更明确的异常
        raise ValueError("Cannot encode None value")
    obj = hashlib.md5()
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()

class admin_loginmodel(BootStrapForm):
    name=forms.CharField(max_length=30,label="用户名",required=True,widget=forms.TextInput)
    password=forms.CharField(max_length=30,label="密码",required=True,widget=forms.PasswordInput)
    def clean_password(self):
        pwd=self.cleaned_data.get("password")
        pwd=md5(pwd)  
        return pwd   


    
def user_login(request):
    if request.method=="GET":
        form=admin_loginmodel()
        active_bg=models.background.objects.filter(is_img=1).first()
        return render(request,"background.html",{"form":form,"active_bg":active_bg})
    form=admin_loginmodel(data=request.POST)
    if form.is_valid():
        data=models.Person.objects.filter(**form.cleaned_data).first()
        if data:
            
            request.session["info"]={"id":data.id,"name":data.name}
            request.session.set_expiry(7200)
            name=request.session.get('info')
            if not name:
                return HttpResponse("登录")
            date=name.get('name')
            logger.info(f"用户{date}登录系统")
            return redirect('/miao/')
        form.add_error("password","用户名或密码错误")
    return render(request,"background.html",{"form":form})

def miao(request):
    name = request.session.get("info", {}).get("name")
    
    try:
        person = models.Person.objects.select_related("room").get(name=name)
        room = person.room  # 拿到房间对象
        
        room_num = person.room.room_name
       
        room_dorm = person.room.dorm
        

        # 费用记录筛选（费用细则）
        room_dian_fees = room.fees.filter(feetype__name="电费")
        room_water_fees = room.fees.filter(feetype__name="水费")
        room_cold_fees= room.fees.filter(feetype__name="空调费")
        room_home_fees= room.fees.filter(feetype__name="房费")

        # 资源使用量筛选（假设res模型有amount字段存储用量）
        res_dian = room.res.filter(feetype__name="电费").first()  # 取第一条用量记录
        res_water = room.res.filter(feetype__name="水费").first()
       

        # 电费分摊记录 → 计算总分摊金额
        dian_sharings = models.feesharing.objects.filter(
            fee_record__in=room_dian_fees,  
            occupancyrecord__user=person  # 关联当前用户（需确认occupancyrecord的外键字段）
        )
        total_dian_sharing =round (sum(Decimal(s.feesharings) for s in dian_sharings) if dian_sharings else 0,2)

        cold_sharings = models.feesharing.objects.filter(
            fee_record__in=room_cold_fees,  
            occupancyrecord__user=person  # 关联当前用户（需确认occupancyrecord的外键字段）
        )
        total_cold_sharing =round (sum(Decimal(s.feesharings) for s in cold_sharings) if cold_sharings else 0,2)
        home_sharings = models.feesharing.objects.filter(
            fee_record__in=room_home_fees, 
            occupancyrecord__user=person  # 关联当前用户（需确认occupancyrecord的外键字段）
        )
        total_home_sharing =round (sum(Decimal(s.feesharings) for s in home_sharings) if home_sharings else 0,2)

        # 水费分摊记录 → 计算总分摊金额
        water_sharings = models.feesharing.objects.filter(
            fee_record__in=room_water_fees,  
            occupancyrecord__user=person
        )
        total_water_sharing = sum(Decimal(s.feesharings) for s in water_sharings) if water_sharings else 0
        print(water_sharings)
        print(dian_sharings)
        total=round(total_dian_sharing+total_water_sharing+total_cold_sharing+total_home_sharing,2)
        not_status=round(models.feesharing.objects.filter(status="0",occupancyrecord__user=person).aggregate(total=Sum("feesharings"))["total"]or Decimal("0"),2)
        status=round(models.feesharing.objects.filter(status="1",occupancyrecord__user=person).aggregate(total=Sum("feesharings"))["total"]or Decimal("0"),2)
        try:
        # 第107行
            rate=round(Decimal(status)/Decimal(total)*100 ,2)
        except DivisionByZero:
        # 当发生除零错误时，执行这里的代码
            fee_per_person = Decimal('0.00')
        
        m1=models.feesharing.objects.filter(occupancyrecord__user=person,status="1",fee_type__name="电费").first()
        m2=models.feesharing.objects.filter(occupancyrecord__user=person,status="1",fee_type__name="水费").first()
        m3=models.feesharing.objects.filter(occupancyrecord__user=person,status="1",fee_type__name="房费").first()
        m4=models.feesharing.objects.filter(occupancyrecord__user=person,status="1",fee_type__name="空调费").first()
        ##费用列表
        list=models.feesharing.objects.filter(occupancyrecord__user=person)
        rate_home=round(Decimal("200")/Decimal(total)*100 ,2)
        rate_cold=round(Decimal("150")/Decimal(total)*100 ,2)
        rate_water=round(Decimal(total_water_sharing)/Decimal(total)*100 ,2)
        rate_dian=round(Decimal(total_dian_sharing)/Decimal(total)*100 ,2)
        ##列表日期
        fee_queryset = models.feesharing.objects.filter(occupancyrecord__user=person).order_by('-start_date')  # 按开始日期倒序

    # 2. 整理数据：提取每个记录的日期和其他字段，组成列表套字典
        fee_records = []
        for record in fee_queryset:
        # 处理状态（将"1"/"0"转换为布尔值，方便前端判断）
            is_paid = record.status == "1"  # True 表示已缴纳，False 表示待缴纳
        
        # 整理单条记录的数据（包含日期）
            fee_records.append({
                "fee_type": record.fee_type.name,  # 费用类型名称（如"房费"）
                "feesharings": record.feesharings,  # 分摊金额
                "start_date": record.start_date,    # 开始计费日期
                "end_date": record.end_date,        # 截止日期
                "is_paid": is_paid                  # 是否缴纳（布尔值）
            })
        
        

    except models.Person.DoesNotExist:
        return HttpResponse(f"没有找到{name}的信息")

    # 传给前端：变量名与模板完全一致，传递计算后的金额
    return render(request, "miao.html", {
        "room_num": room_num,
        "room_dorm": room_dorm,
        "dian_sharing_amount": total_dian_sharing,  # 电费总分摊金额
        "water_sharing_amount": total_water_sharing,  # 水费总分摊金额
        "res_dian_amount": res_dian.usege if res_dian else 0,  # 电费用量
        "res_water_amount": res_water.usege if res_water else 0,  # 水费用量
        "room_dian_fee_total": room_dian_fees.first().amount if room_dian_fees else 0,  # 电费总费用
        "room_water_fee_total": room_water_fees.first().amount if room_water_fees else 0,  # 水费总费用
        "total":total,
        "status":status,
        "not_status":not_status,
        "rate":rate,
        "m1":m1,
        "m2":m2,
        "m3":m3,
        "m4":m4,
        "list":list,
        "rate_home":rate_home,
        "rate_cold":rate_cold,  
        "rate_water":rate_water,
        "rate_dian":rate_dian,
        "total_cold_sharing":total_cold_sharing,
        "total_home_sharing":total_home_sharing,
        "fee_records": fee_records,
    })

def logout(request):
    
    name=request.session.get("info",{}).get("name")
    if not name:
        return HttpResponse("请登录")
    logger.info(f"用户{name}退出登录")
    request.session.clear()
    return redirect("/user/login/")

logger=logging.getLogger("management")


class ResetPasswordForm(forms.ModelForm):
    # 确认新密码字段（仅用于验证，不关联模型）
    confirm_password = forms.CharField(
        label="确认新密码",
        widget=forms.PasswordInput(render_value=True)  # 密码错误时保留输入
    )

    class Meta:
        model = models.Person
        fields = ["password"]  # 仅需新密码字段（模型中存储密码的字段）
        labels = {
            "password": "新密码"  # 显示为“新密码”而非默认的“password”
        }
        widgets = {
            "password": forms.PasswordInput(render_value=True)  # 密码框，错误时保留输入
        }

    def clean_password(self):
        """验证新密码不能与原密码相同"""
        new_password = self.cleaned_data.get("password")  # 获取明文新密码
        new_password_md5 = md5(new_password)  # 加密新密码
        
        # 对比新密码加密后是否与数据库中原密码一致
        if self.instance.password == new_password_md5:
            raise forms.ValidationError("新密码不能与原密码相同")
        
        return new_password  # 返回明文，后续在save中统一加密

    def clean(self):
        """验证两次输入的新密码是否一致"""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password != confirm_password:
            raise forms.ValidationError("两次输入的密码不一致")
        
        return cleaned_data

    def save(self, commit=True):
        """保存时加密新密码"""
        admin = self.instance  # 当前登录用户实例
        admin.password = md5(self.cleaned_data["password"])  # 加密后更新密码
        if commit:
            admin.save()
        return admin

def user_reset(request):
    # 验证登录状态
    info = request.session.get("info")
    if not info:
        return HttpResponse("请先登录")
    
    user_id = info.get("id")
    user_obj = models.Person.objects.filter(id=user_id).first()
    if not user_obj:
        return HttpResponse("用户不存在")

    if request.method == "GET":
        # 初始化表单，关联当前用户实例（用于验证原密码）
        form = ResetPasswordForm()
        return render(request, "add_area.html", {
            "title": f"重置密码 - {user_obj.name}",
            "form": form
        })

    # 处理密码重置提交
    form = ResetPasswordForm(data=request.POST, instance=user_obj)
    if form.is_valid():
        form.save()  # 保存加密后的新密码
        logger.info(f"{user_obj.name} 重置了密码")
        request.session.flush()  # 清除session，强制重新登录
        return redirect("/user/login/")
    
    # 表单验证失败，回显错误
    return render(request, "add_area.html", {
        "title": f"重置密码 - {user_obj.name}",
        "form": form
    })