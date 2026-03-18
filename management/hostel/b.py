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

# class upload_a_imgmodel(BootStrapModelForm):
#     class Meta:
#         model=models.a_img
#         fields=["a_img"]

# def upload_a_img(request):
#     if request.method=="POST":
#         form=upload_a_imgmodel(request.POST,request.FILES)
#         if form.is_valid():
#             new_bg=form.save(commit=False)
#             new_bg.is_img=True
#             form.save()
#             return redirect("/user_img/")
#     form=upload_a_imgmodel()
#     active_img=models.a_img.objects.filter(is_img=True).first()
#     context={
#         "form":form,
#         "active_img":active_img
#     }
#     return render(request,"abc.html",context)

# def user_img(request):
#     active_img=models.a_img.objects.filter(is_img=True).first()
#     return render(request,"upload_a_img.html",{"active_img":active_img})




