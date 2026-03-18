from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from datetime import date, timedelta

from hostel.person import parse_date
from decimal import Decimal,DecimalException
from django.urls import reverse 
logger=logging.getLogger('management')

# simple_card/views.py（修改后，贴合房间类型业务）
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import room_type  # 导入你的 room_type 模型

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = room_type
        fields = ['name', 'bed_count', 'money', 'dorm',"effective_date"]
   
def add_room_type(request):
    # 从数据库中获取所有房间类型
    all_room_types =models.room_type.objects.filter(status=True)
    all_areas=models.dorm.objects.all()

    if request.method == 'POST':
        # 获取表单提交的房间类型名称和床位数量
        type_name = request.POST.get('type_name', '').strip()
        bed_count = request.POST.get('bed_count', '').strip()
        # cdate=request.POST.get('cdate','').strip()
        money=request.POST.get('money','').strip()
        dorm_id=request.POST.get('dorm_id','').strip()

        if type_name and bed_count.isdigit()and dorm_id:  # 简单验证：名称不为空，床位是数字
            # 创建并保存新的房间类型
            new_room_type = models.room_type(
                name=type_name,
                bed_count=int(bed_count),
                # cdate=parse_date(cdate),
                money=Decimal(money),
                dorm_id=int(dorm_id)
            )
            new_room_type.save()
            messages.success(request, f'房间类型 "{type_name}" 已成功添加！')
            return redirect("statusUI") 

    return render(request, 'room_type_file.html', {'room_types': all_room_types,"areas":all_areas})

def room_type(request):
    search_data=request.GET.get('q','')
    query=models.room_type.objects.all()
    if search_data:
        query=query.filter(name__contains=search_data)
    page_num=request.GET.get('page',1)
    paginator=Paginator(query,5)
    
    try:
        c_page=paginator.page(page_num)
    except PageNotAnInteger:
        c_page=paginator.page(1)
    except EmptyPage:
        c_page=paginator.page(paginator.num_pages)
    if paginator.num_pages>=3:
        page_nums=[1,2,3]
    else:
        page_nums=paginator.page_range
    context={
        'c_page':c_page,
        'search_data':search_data,
        'paginator':paginator,
        'page_nums':page_nums,

    }
    return render(request,'room_type.html',context)

def delete_room_type(request,id):
    page_num=request.GET.get('page',1)
    page_num=int(page_num)
    row_object=models.room_type.objects.filter(id=id).first()
    if not row_object:
        return HttpResponse("房型不存在，无法删除")
    row_object.delete()
    return redirect('/hostel/room_type?page=page_num')

def delete_all_room_type(request):
    page_num=request.GET.get('page',1)
    page_num=int(page_num)
    if request.method=='POST':
        ids=request.POST.getlist('ids')
        if not ids:
            messages.error('未选择删除的人员')
        try:
            models.room_type.objects.filter(id__in=ids).delete()
            messages.success(request,f'成功删除{len(ids)}条房型记录')
        except Exception as e:
            messages.error(request,f'删除失败，错误信息：{e}')
        return redirect(f'/hostel/room_type/')
    return HttpResponse("仅支持POST请求")

class RoomTypeEditForm(forms.ModelForm):
    status = forms.BooleanField(
        label='是否启用',
        widget=forms.CheckboxInput(attrs={'class': ''}),  # 清空样式
        required=False  # 非必填（根据你的需求调整）
    )

    class Meta:
        model=models.room_type
        fields=["dorm",'name','bed_count',"money"]

def edit_room_type(request,id):
    
    row_object=models.room_type.objects.filter(id=id).first()
    title='编辑房型-{}'.format(row_object.name)
    if not row_object:
        return HttpResponse("房型不存在，无法编辑")
    if request.method=='GET':
        form=RoomTypeEditForm(instance=row_object)
        return render(request,'edit_room_type.html',{'form':form,'title':title})
    form=RoomTypeEditForm(data=request.POST,instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/hostel/room_type/')
    return render(request,'edit_room_type.html',{'form':form ,'title':title})



    

