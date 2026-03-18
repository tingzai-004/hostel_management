from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator
import io
from django.contrib import messages


class Backgroundmodel(BootStrapModelForm):
    bootstrap_exclude=["img"]
    class Meta:
        model=models.background
        fields=["img"]

def upload_back(request):
    if request.method=="POST":
        form=Backgroundmodel(request.POST,request.FILES)
        if form.is_valid():
            models.background.objects.update(is_img=False)
            new_bg=form.save(commit=False)
            new_bg.is_img=True
            new_bg.save()
            return redirect('/upload_back/')
    else:
        form=Backgroundmodel()
    active_bg=models.background.objects.filter(is_img=True).first()
    context={
        "form":form,
        "active_bg":active_bg
    }
    return render(request,"upload_back.html",context)

class Moneymodel(BootStrapModelForm):
    bootstrap_exclude=["img"]
    class Meta:
        model=models.money_upload
        fields=["name","img"]
def money_upload(request):
    
    if request.method=="POST":
        form=Moneymodel(request.POST,request.FILES)
        if form.is_valid():
            new_bg=form.save(commit=False)
            new_bg.is_img=True
            form.save()
            messages.info(request,"提交成功！")
            # return redirect("/miao/")
        
    else:
        form=Moneymodel()
    active_bg=models.money_upload.objects.filter(is_img=True).first()
    return render(request,"add_money.html",{"form":form,"active_bg":active_bg})

