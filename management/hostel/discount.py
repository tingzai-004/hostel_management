from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.contrib import messages
from hostel.person import parse_date
from decimal import Decimal,DecimalException
from decimal import ROUND_HALF_UP
logger=logging.getLogger('management')

def discount_views(request):
    search_data=request.GET.get('q','')
    query=models.discount.objects.all()
    if search_data:
        query=query.filter(fee_type__name__contains=search_data)
    paginator=Paginator(query,5)
    page_num=request.GET.get('page',1)
    try:
        c_page=paginator.page(page_num)

    except PageNotAnInteger:
        c_page=paginator.page(1)
    except EmptyPage:
        c_page=paginator.page(paginator.num_pages)
    if paginator.num_pages>3:
        page_nums=[1,2,3]
    else:
        page_nums=paginator.page_range
    
    context={
        'c_page':c_page,
        'page_nums':page_num,
        'search_data':search_data,
        'paginator':paginator,
        'page_nums':page_nums,
    }
    return render(request,'discount_views.html',context)

def delete_discount(request,id):
    page_nums=request.GET.get('page',1)
    page_nums=int(page_nums)
    row_obj=models.discount.objects.filter(id=id).first()
    if not row_obj:
        return HttpResponse('删除的数据不存在')
    try:
        row_obj.delete()
        messages.info(request,"成功删除一条折扣率记录")
        logger.info(f"{request.session.get('info',{}).get('name')}删除了一条折扣率记录")
        return redirect(f'/hostel/discount?page={page_nums}')
    except Exception as e:
        messages.error(request,"删除失败")

class editDiscountModelForm(BootStrapModelForm):
    bootstrap_exclude=["status"]
    class Meta:
        model=models.discount
        fields=['rate',"check_in_date","status"]
    
def edit_discount(request,id):
    page_nums=request.GET.get('page',1)
    page_nums=int(page_nums)
    row_obj=models.discount.objects.filter(id=id).first()
    titel="修改-{}折扣率".format(row_obj.fee_type.name)
    if not row_obj:
        return HttpResponse('编辑的数据不存在')
    if request.method=='GET':
        form=editDiscountModelForm(instance=row_obj)
        context={
            'row_obj':row_obj,
            'form':form,
            'titel':titel,
        }
        return render(request,'add_area.html',context)
    form=editDiscountModelForm(data=request.POST,instance=row_obj)
    discount_rate=request.POST.get('rate')
    try:
        discount_rate=Decimal(discount_rate).quantize(Decimal('0.00'),rounding=ROUND_HALF_UP)

    except DecimalException:
        messages.error(request,'折扣率格式不正确，请输入数字类型')
    row_obj.rate=discount_rate
    try:
        row_obj.save()
        messages.success(request,f'{row_obj.fee_type}折扣率修改成功')
        logger.info(f"{request.session.get('info',{}).get('name')}修改了一条折扣率记录")
        return redirect(f'/hostel/discount?page={page_nums}')
    except Exception as e:
        messages.error(request,'折扣率修改失败，请重试')
        return redirect(f'/hostel/discount/edit/{id}?page={page_nums}')

class DiscountModelForm(BootStrapModelForm):
    bootstrap_exclude=["status"]
    class Meta:
        model=models.discount
        fields=['fee_type','rate','check_in_date',"date","status"]

def add_discount(request):
    title="添加折扣率"
    if request.method =="GET":
        form=DiscountModelForm()
        return render(request,'add_area.html',{'title':title,'form':form})
    form=DiscountModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(request,'折扣率添加成功')
        logger.info(f"{request.session.get('info',{}).get('name')}添加了一条折扣率记录")
        return redirect('/hostel/discount')
    return render(request,'add_area.html',{'title':title,'form':form})

def del_all_discount(request):
    if request.method=="POST":
        ids=request.POST.getlist('ids')
        if not ids:
            messages.error(request,"请选择数据")
        try:
            models.discount.objects.filter(id__in=ids).delete()
        except Exception as e:
            messages.error(request,"删除失败")
        return redirect('/hostel/discount/')
    return redirect('/hostel/discount/')
    
    


        



