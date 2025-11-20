from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import area ,dorm
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator
from django.db.models import Count

def statusUI(request):
    total = models.Room.objects.count()
    normal_count = models.Room.objects.filter(room_status_id=2).count()
    full_count = models.Room.objects.filter(room_status_id=1).count()
    repair = models.Room.objects.filter(room_status_id=3).count()
    dath=models.Room.objects.filter(room_status_id=4).count()  # 修复：加括号()
    all_room_types=models.room_type.objects.all()
    # room_two=models.room_type.objects.filter(name="2人间").first()
    # room_six=models.room_type.objects.filter(name="6人间").first()
    # # bed_count_two=room_two.bed_count
    # bed_count_six=room_six.nums

    gender1=models.Room.objects.filter(gender="1").count()
    gender2=models.Room.objects.filter(gender="2").count()
    gender3=models.Room.objects.filter(gender="1",room_status_id=2).count()
    gender4=models.Room.objects.filter(gender="2",room_status_id=2).count()
    records = models.occupancyrecord.objects.select_related('user__gender').all()

# 然后在内存中进行过滤和计数
    women = records.filter(status='0',user__gender_id="2").count()
    men = records.filter(status='0',user__gender_id="1").count()

    new_type_id = request.GET.get("new_type_id")
    new_room_count = None
    new_type_name = None
    
    if new_type_id:
        # 根据ID查询新添加的房型
        new_type = models.room_type.objects.get(id=new_type_id)
        new_type_name = new_type.name
        new_room_count = models.Room.objects.filter(room_type=new_type).count()
        # room_count2 = models.Room.objects.filter(status="0",room_type=new_type).count()




    if request.method == "GET":
        current_status = request.GET.get("status", "")
        current_dorm = request.GET.get("dorm", "")
        current_area=request.GET.get('area',"")

        # 初始查询所有房间
        rooms = models.Room.objects.all()

        # 按状态筛选（注意用 room_status_id 匹配数字ID）
        if current_status:
            rooms = rooms.filter(room_status_id=current_status)

        # 按楼栋筛选
        if current_dorm:
            rooms = rooms.filter(dorm=current_dorm)

        if current_area:
            rooms=rooms.filter(dorm__area__name=current_area)

        # 传递筛选后的 rooms 到模板
        context = {
            "total": total,
            "normal_count": normal_count,
            "full_count": full_count,
            "repair": repair,
            "rooms": rooms,
            "current_status": current_status,
            "current_dorm": current_dorm,
            "current_area":current_area,
            "dath":dath,
            # "bed_count":bed_count_two,
            # "bed_count_six":bed_count_six,
            "room_types":all_room_types,
            "gender1":gender1,
            "gender2":gender2,
            "gender3":gender3,
            "gender4":gender4,
            "women":women,
            "men":men,
            "all_room_types": all_room_types,
            "new_type_name": new_type_name,  # 新添加的房型名称
            "new_room_count": new_room_count,
            # "room_count": room_count2,

        }
        return render(request, "statusUI.html", context)