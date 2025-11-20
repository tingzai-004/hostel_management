from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Sum,Count
import hashlib
from django.contrib import messages

logger = logging.getLogger('menagement')

class checkoutmodel(BootStrapModelForm):
    
    class Meta:
        model=models.occupancyrecord
        fields=['check_in_date','check_out_date','status']
    def save(self, commit=True):
        # 获取当前实例
        instance = super().save(commit=False)
        # 自动设置状态为 '1' (退宿)
        instance.status = '1'
        if commit:
            instance.save()
        return instance

##退宿
def checkout_occupancyrecord(request,id):
    
    row_object=models.occupancyrecord.objects.filter(id=id).first()
    
    if row_object==None:
        return HttpResponse("要操作数据不存在")
    title="退宿-{}".format(row_object.user.name)
    if request.method=="GET":
        
        form=checkoutmodel(instance=row_object)
        return render(request,"add_area.html",{"form":form,"titel":title})
    form=checkoutmodel(data=request.POST,instance=row_object)
    if form.is_valid():
        data=request.session.get('info')
        if data==None:
            return HttpResponse("请先登录")
        name=data.get('name')
        
        new_peopel=form.save()
        room=new_peopel.room
        current_people=models.occupancyrecord.objects.filter(room=room,status='0').count()
        room.people=current_people
        related_people=int("".join(filter(str.isdigit,room.room_perpe)))
        if current_people<related_people:
            room.room_status=models.room_status.objects.get(name="可住")
            messages.success(request, f'退宿成功，当前房间入住人数为{current_people}，房间状态已更新为可住')
            room.save()
        else:
            room.room_status=models.room_status.objects.get(name="住满")
            messages.success(request, f'退宿成功，当前房间入住人数为{current_people}，房间状态为已满')
            room.save()

        logger.info(f"{request.session.get('info', {}).get('name')} 将 员工: {row_object.user}从 房间: {room.room_name}退宿")
        return redirect("/hostel/checkout_record/")
    return render(request,"add_area.html",{"form":form,"error":form.errors,"titel":title})

def checkout_record(request):
    search_data = request.GET.get('q', '')
    query = models.occupancyrecord.objects.filter(status="1")
    if search_data:
        query = query.filter(user__name__contains=search_data)  # 搜索过滤

    # 2. 分页配置（每页5条）
    paginator = Paginator(query, 5)
    page_num = request.GET.get('page', 1)  # 拿页码，默认1

    # 3. 关键：容错处理（不管页码错成啥样，都返回有效页）
    try:
        c_page = paginator.page(page_num)
        
    except PageNotAnInteger:  # 页码不是数字（比如?page=abc）
        c_page = paginator.page(1)  # 给第1页
    except EmptyPage:  # 页码超出范围（比如总1页，?page=2）
        c_page = paginator.page(paginator.num_pages)  # 给最后1页
    if paginator.num_pages <= 3:
            page_nums = paginator.page_range  # 所有页码
    else:
            page_nums = [1, 2, 3] 

    # 4. 传数据到模板
    return render(request, 'del_occupancyrecord.html', {
        'c_page': c_page,
        'paginator': paginator,
        'search_data': search_data,
        "page_nums":page_nums,
    })

def delete_checkout(request, id):
    row_object = models.occupancyrecord.objects.filter(id=id).first()
    if row_object is None:
        return HttpResponse("要删除的数据不存在")
    data = request.session.get('info')
    if data is None:
        return HttpResponse("请先登录")
    name = data.get('name')
    logger.info('%s了删除了%s的住宿记录' % (name, row_object.user))
    row_object.delete()
    # 获取当前页码，删除后返回该页
    page = request.GET.get('page', 1)
    return redirect(f'/hostel/checkout_record/?page={page}')

def edit_checkout(request,id):
    row_object=models.occupancyrecord.objects.filter(id=id).first()
    if row_object==None:
        return HttpResponse("要操作数据不存在")
    if request.method=="GET":
        title="编辑退宿记录-{}".format(row_object.user.name)
        form=checkoutmodel(instance=row_object)
        return render(request,"add_area.html",{"form":form,"titel":title})
    form=checkoutmodel(data=request.POST,instance=row_object)
    if form.is_valid():
        data=request.session.get('info')
        if data==None:
            return HttpResponse("请先登录")
        name=data.get('name')
        logger.info('%s了楼栋数更新了%s的退宿记录'%(name,row_object.user))
        form.save()
        return redirect("/hostel/checkout_record/")
    return render(request,"add_area.html",{"form":form,"error":form.errors,"titel":title})
