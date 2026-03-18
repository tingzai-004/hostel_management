from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import io
import hashlib
logger=logging.getLogger("management")
def md5(data_string):
    if data_string is None:
        # 可以选择返回一个默认值，或者抛出更明确的异常
        raise ValueError("Cannot encode None value")
    obj = hashlib.md5()
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()


def admin_list(request):
    search_data = request.GET.get('q', '')
    query = models.Admin.objects.all()
    if search_data:
        query = query.filter(name__contains=search_data)  # 搜索过滤

    # 2. 分页配置（每页5条）
    paginator = Paginator(query, 5)
    page_num = request.GET.get('page', 1)  # 拿页码，默认1

    # 3. 关键：容错处理（不管页码错成啥样，都返回有效页）
    try:
        c_page = paginator.page(page_num)
        if paginator.num_pages <= 3:
            page_nums = paginator.page_range  # 所有页码
        else:
            page_nums = [1, 2, 3] # 尝试拿指定页
    except PageNotAnInteger:  # 页码不是数字（比如?page=abc）
        c_page = paginator.page(1)  # 给第1页
    except EmptyPage:  # 页码超出范围（比如总1页，?page=2）
        c_page = paginator.page(paginator.num_pages)  # 给最后1页

    # 4. 传数据到模板
    return render(request, 'admin_list.html', {
        'c_page': c_page,
        'paginator': paginator,
        'search_data': search_data,
        "title":"admin人员列表",
        "page_nums":page_nums,
    })

class adminmodel(BootStrapModelForm):
    bootstrap_exclude=["is_super","is_active"]
    class Meta:
        model=models.Admin
        fields=["name","phone","email","password",'is_super',"is_active","permissions"]
    def clean_password(self):
        pwd=self.cleaned_data.get("password")
        md5_pwd=md5(pwd)
        return md5_pwd


def add_admin(request):
    if request.method=="GET":
        title="添加管理员"
        form=adminmodel()
        return render(request,"add_area.html",{"form":form,"title":title})
    form=adminmodel(data=request.POST)
    if form.is_valid():
        # data=request.session.get('info')
        # if data==None:
        #     return HttpResponse("请先登录")
        # name=data.get('name')
        # logger.info('超级管理员%s添加了%s为管理员'%(name,form.cleaned_data.get('name')))
        form.save()
        return redirect("/admin_list/")
    return render(request,"add_area.html",{"form":form,"error":form.errors,'title':"添加管理员"})

def delete_admin(request,id):
    data=request.session.get('info')
    if data==None:
            return HttpResponse("请先登录")
    name=data.get('name')
    page_num=request.GET.get("page",1)
    
    page_num=int(page_num)
    row_obj=models.Admin.objects.filter(id=id).first()
    if row_obj:
        logger.info(f'{name}删除了管理员{row_obj.name}记录')
        row_obj.delete()
        return redirect(f'/admin_list/?page={page_num}')
    return HttpResponse("数据不存在")

class editoradminmodel(BootStrapModelForm):
    bootstrap_exclude=["is_super","is_active"]
    class Meta:
        model=models.Admin
        fields=["name","phone","email",'is_super',"is_active","permissions"]


def editor_admin(request,id):
    row_obj=models.Admin.objects.filter(id=id).first()
    if request.method=="GET":
        title='编辑-{}的信息'.format(row_obj.name)
        form=editoradminmodel(instance=row_obj)
        return render(request,'add_area.html',{'form':form,'title':title})
    form=editoradminmodel(data=request.POST,instance=row_obj)
    if form.is_valid():
        data=request.session.get('info')
        if data==None:
            return HttpResponse("请先登录")
        name=data.get('name')
        logger.info('超级管理员%s编辑了%s管理的信息'%(name,form.cleaned_data.get('room_name')))
        form.save()
        return redirect('/admin_list/')
    else:
        return render(request,'add_area.html',{'form':form,'error':form.errors})

    