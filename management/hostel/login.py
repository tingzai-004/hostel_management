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
from django.contrib import messages
def md5(data_string):
    if data_string is None:
        # 可以选择返回一个默认值，或者抛出更明确的异常
        raise ValueError("Cannot encode None value")
    obj = hashlib.md5()
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()

    

logger=logging.getLogger('management')


class admin_loginmodel(BootStrapForm):
    name=forms.CharField(max_length=30,label="用户名",required=True,widget=forms.TextInput)
    password=forms.CharField(max_length=30,label="密码",required=True,widget=forms.PasswordInput)
    def clean_password(self):
        pwd=self.cleaned_data.get("password")
        pwd=md5(pwd)  
        return pwd   


    
def admin_login(request):
    if request.method=="GET":
        form=admin_loginmodel()
        active_bg=models.background.objects.filter(is_img=1).first()
        return render(request,"background.html",{"form":form,"active_bg":active_bg})
    form=admin_loginmodel(data=request.POST)
    if form.is_valid():
        data=models.Admin.objects.filter(**form.cleaned_data).first()
        if data:
            
            request.session["info"]={"id":data.id,"name":data.name,"is_super":data.is_super}
            request.session.set_expiry(7200)
            name=request.session.get('info')
            if not name:
                return HttpResponse("登录")
            date=name.get('name')
            logger.info(f"管理员{date}登录用户系统")
            return redirect('/statusUI/')
        form.add_error("password","用户名或密码错误")
        
    return render(request,"background.html",{"form":form})

class upmodelform(BootStrapModelForm):
    class Meta:
        model=models.background
        fields="__all__"


def upload(request):
    if request.method=="GET":
        form=upmodelform()
        return render(request,"abc.html",{"form":form})
    
    form=upmodelform(data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return HttpResponse("CG")
    return render(request,"abc.html",{"form":form})


def bg(request):
    
    form=models.background.objects.filter(name="123")
    return render(request,"moban.html",{"form":form})
#状态
def statuUI(request):
    if request.method=="GET":
        return render(request,"statusUI.html")
#注销   
def logout(request):
    name=request.session.get('info')
    if name:
        date=name.get('name')

        
        logger.info(f"{date}退出登录")
        request.session.clear()
        return redirect("/login/")
    else:
        return HttpResponse("请登录")