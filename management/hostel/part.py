from django.shortcuts import get_object_or_404, render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator
import io
from .login import md5
import logging
from django.db.models import Count,Sum
import os
from django.conf import settings
from datetime import datetime
import random
import string
from decimal import Decimal

logger=logging.getLogger("management")

class ResetPasswordForm(forms.ModelForm):
    # 确认新密码字段（仅用于验证，不关联模型）
    confirm_password = forms.CharField(
        label="确认新密码",
        widget=forms.PasswordInput(render_value=True)  # 密码错误时保留输入
    )

    class Meta:
        model = models.Admin
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

def admin_reset(request):
    # 验证登录状态
    info = request.session.get("info")
    if not info:
        return HttpResponse("请先登录")
    
    user_id = info.get("id")
    user_obj = models.Admin.objects.filter(id=user_id).first()
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
        return redirect("/login/")
    
    # 表单验证失败，回显错误
    return render(request, "add_area.html", {
        "title": f"重置密码 - {user_obj.name}",
        "form": form
    })

from decimal import Decimal, ROUND_HALF_UP
##报表
def table(request):
    
    current_status=request.GET.get("current_status","")
    current_month=request.GET.get("current_month","")
    current_area=request.GET.get("current_area","")
    current_fee_type=request.GET.get("current_fee_type","")
    power=models.fee_record.objects.filter(feetype="4").aggregate(power=Sum("amount"))["power"]or 0
    water=models.fee_record.objects.filter(feetype="3").aggregate(power=Sum("amount"))["power"]or 0
    cold=models.fee_record.objects.filter(feetype="2").aggregate(power=Sum("amount"))["power"]or 0
    home=models.fee_record.objects.filter(feetype="1").aggregate(power=Sum("amount"))["power"]or 0
    
    
 # 2. 基础查询：获取feesharing的所有数据（确认有数据）
    fees = models.feesharing.objects.all()
    print("原始数据量：", fees.count())  # 控制台看是否有数据（比如输出10）

    # 3. 筛选逻辑（逐个排查，先只开一个筛选测试）
    # 状态筛选（0=未缴，1=已缴）
    if current_status in ["0", "1"]:  # 只接受有效状态值
        fees = fees.filter(status=current_status)
        print(f"状态筛选后数据量：{fees.count()}")  # 看是否有数据

    # 费用类型筛选（外键ID）
    if current_fee_type.isdigit():  # 确保是数字ID
        fees = fees.filter(fee_type_id=current_fee_type)
        print(f"类型筛选后数据量：{fees.count()}")

    if current_month:
        try:
            year, month = current_month.split("年")
            month = month.replace("月", "").zfill(2)
            month_str = f"{year}-{month}"
            fees = fees.filter(end_date__startswith=month_str)
            print(f"月份筛选后数据量：{fees.count()}")
        except:
            pass  # 格式错误时不筛选



    # 4. 分页（无论如何，form必须有值）
    paginator = Paginator(fees, 10)
    page = request.GET.get('page', 1)
    form = paginator.get_page(page)  # 即使筛选后无数据，form也会有分页对象
    print(f"最终分页后的数据量：{form.object_list.count()}")  # 看是否有数据

    # 5. 其他统计数据（保持不变）
    total1_sum = models.fee_record.objects.aggregate(total=Sum("amount"))["total"]
    # 处理空值 + 强制转为 Decimal
    total1 = Decimal(str(total1_sum)) if total1_sum is not None else Decimal("0")
    # 保留2位小数
    total1 = total1.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    # 2. 已收费用（同上处理）
    total_count_sum = models.feesharing.objects.filter(status=1).aggregate(total=Sum("feesharings"))["total"]
    total_count = Decimal(str(total_count_sum)) if total_count_sum is not None else Decimal("0")
    total_count = total_count.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    # 3. 未收费用（同上处理）
    total_not_sum = models.feesharing.objects.filter(status=0).aggregate(total=Sum("feesharings"))["total"]
    total_not = Decimal(str(total_not_sum)) if total_not_sum is not None else Decimal("0")
    total_not = total_not.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    # 4. 计算百分比（彻底用 float 处理，避免 Decimal 除法问题）
    total1_float = float(total1)  # 转为 float
    rate = round((float(total_count) / total1_float) * 100, 2) if total1_float != 0 else 0.0
    rate_2 = round((float(total_not) / total1_float) * 100, 2) if total1_float != 0 else 0.0

    people = models.Room.objects.aggregate(people=Sum("people"))["people"] or Decimal ("0")
    room_sum = models.Room.objects.aggregate(room_sum=Count("id"))["room_sum"] or Decimal ("0")
   

# 计算概率（带异常处理）
   
    
    # 6. 上下文：传给前端的是筛选+分页后的form
    context = {
        "total1": total1,
        "total_count": total_count,
        "total_not": total_not,
        "people": people,
        "room_sum": room_sum,
        "rate": rate,
        "rate_2": rate_2,
        "form": form,  # 用筛选后的分页数据
        "paginator": paginator,
        
        "current_status": current_status,
        "current_month": current_month,
        "current_area": current_area,
        "current_fee_type": current_fee_type,
        "power":power,
        "water":water,
        "home":home,
        "cold":cold,
    }
    
    return render(request, "table.html", context)
        
    
class Usermodel(BootStrapModelForm):
    bootstrap_exclude=["img"]
    img=forms.CharField(max_length=20,label="头像")
    class Meta:
        model=models.user_img
        fields=["name","img"]
##修改背景
def show_image(request):
    # 查询最新上传的图片（按id倒序，取第一条）
    img = models.background.objects.order_by('-id').first()
    return render(request, 'background.html', {'img': img})

##导出
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

def write_to_excel(data_list, file_path):
    if not data_list:
        workbook = openpyxl.Workbook()
        workbook.save(file_path)
        return
    
    # 中文表头映射
    header_mapping = {
        "id": "编号",
        "oc"
        "room": "房间号",
        "total": "总金额",
        "paid": "缴纳金额",
        "status": "缴纳状态",
        "date": "日期",
    }
    headers = [header_mapping.get(key, key) for key in data_list[0].keys()]
    
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    
    # 写入表头并设置样式
    for col_num, header_name in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header_name
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
    
    # 写入数据
    for row_num, row_data in enumerate(data_list, 2):
        for col_num, header_name in enumerate(headers, 1):
            original_key = list(data_list[0].keys())[col_num - 1]
            value = row_data.get(original_key, "")
            sheet.cell(row=row_num, column=col_num).value = value
    
    # 设置列宽
    for col_num in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_num)
        sheet.column_dimensions[col_letter].width = 20  # 调整为合适宽度
    
    workbook.save(file_path)

def get_random_str(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def peint(request):
    obj_fee = models.fee.objects.all().values()
    fee = list(obj_fee)
    
    excel_name = f"students_{get_random_str()}.xlsx"
    path = os.path.join(settings.MEDIA_ROOT, excel_name)
    
    write_to_excel(fee, path)
    return HttpResponse("导出成功")
    
def table2(request):
    return render(request,"table2.html")


    
    