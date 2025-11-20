from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

from hostel.person import parse_date
from decimal import Decimal,DecimalException
from django.urls import reverse 
logger=logging.getLogger('management')

# simple_card/views.py（修改后，贴合房间类型业务）
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import room_type  # 导入你的 room_type 模型

def room_type_view(request):
    # 从数据库中获取所有房间类型
    all_room_types = room_type.objects.all()

    if request.method == 'POST':
        # 获取表单提交的房间类型名称和床位数量
        type_name = request.POST.get('type_name', '').strip()
        bed_count = request.POST.get('bed_count', '').strip()

        if type_name and bed_count.isdigit():  # 简单验证：名称不为空，床位是数字
            # 创建并保存新的房间类型
            new_room_type = room_type(
                name=type_name,
                bed_count=int(bed_count)
            )
            new_room_type.save()
            messages.success(request, f'房间类型 "{type_name}" 已成功添加！')
            return redirect(reverse("statusUI") + f"?new_type_id={new_room_type.id}")

    return render(request, 'room_type.html', {'room_types': all_room_types})