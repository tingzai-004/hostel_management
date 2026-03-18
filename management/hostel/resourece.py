from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Count,Sum

from hostel.person import parse_date
from decimal import Decimal,DecimalException
import decimal

logger=logging.getLogger('management')
class useagemodel(BootStrapModelForm):
    class Meta:
        model = models.useage
        fields = ['room', 'feetype', 'start', 'end', 'check_in_date', 'check_people']
        exclude = ['usege'] 


def resource_useage_list(request):#资源使用量
    search_data=request.GET.get('q','')
    form=models.useage.objects.all()
    if search_data:
         form=form.filter(room__room_name__contains=search_data)
    page_nums=request.GET.get("page",1)
    paginator=Paginator(form,5)
    page_obj=paginator.get_page(page_nums)
    current=page_obj.number
    total_page=paginator.num_pages
    if total_page<=3:
         display_page=list(range(1,total_page+1))
    else:
        if current<=2:
              display_page=[1,2,3]
        elif current >= total_page - 1:
            display_page = [total_page - 2, total_page - 1, total_page]
        else:
            display_page = [current - 1, current, current + 1]
    try:
         c_page=paginator.page(page_obj)
    except PageNotAnInteger:
         c_page=paginator.page(1)
    except EmptyPage:
         c_page=paginator.page(total_page)

    context={
         "display_page":display_page,
         'c_page':c_page,
         "search_data":search_data,
         "paginator":paginator,
         "titel":"宿舍资源用量记录"
         

    }
         

    

    # 4. 传数据到模板
    return render(request, 'resource_useage.html', context
    )


def add_resource(request):
    if request.method == "GET":
        form = useagemodel()
        return render(request, "add_area.html", {"form": form, "titel": "添加资源用量"})
    
    form = useagemodel(data=request.POST)
    if form.is_valid():
        # 直接保存，模型的 save 方法会自动创建费用记录
        form.save()  # 这里会触发 useage 的 save → create_or_update_fee_record
        return redirect('/hostel/resource_useage/')
    
    # 表单验证失败时返回错误
    return render(request, "add_area.html", {"form": form, "error": form.errors, "titel": "添加资源用量"})

def del_resource(request, id):
    row_object = models.useage.objects.filter(id=id).first()
    if row_object is None:
            return HttpResponse("数据不存在")
    row_object.delete()
    return redirect("/hostel/resource_useage/")

def edit_resource(request, id):
    row_object = models.useage.objects.filter(id=id).first()
    if row_object is None:
            return HttpResponse("要修改的数据不存在")
    if request.method == 'GET':
        titel = "修改-{}".format(row_object.room)
        form = useagemodel(instance=row_object)
        return render(request, 'add_area.html', {"form": form, "titel": titel})
    form = useagemodel(data=request.POST, instance=row_object)
    if form.is_valid():
            form.save()
            return redirect("/hostel/resource_useage/")
    return render(request, 'add_area.html', {"form": form, "error": form.errors, "titel": titel})






