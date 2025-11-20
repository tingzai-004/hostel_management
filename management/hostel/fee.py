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
logger=logging.getLogger('management')

class feetypemodel(BootStrapModelForm):
    class Meta:
        model=models.feetype
        fields=['name','bit','cdate','status','fee']
def feetype(request):#计费类型
    search_data = request.GET.get('q', '')
    query = models.feetype.objects.all()
    if search_data:
        query = query.filter(name__contains=search_data)  # 搜索过滤

    # 2. 分页配置（每页5条）
    paginator = Paginator(query, 5)
    page_num = request.GET.get('page', 1)  # 拿页码，默认1

    # 3. 关键：容错处理（不管页码错成啥样，都返回有效页）
    try:
        c_page = paginator.page(page_num)  # 尝试拿指定页
    except PageNotAnInteger:  # 页码不是数字（比如?page=abc）
        c_page = paginator.page(1)  # 给第1页
    except EmptyPage:  # 页码超出范围（比如总1页，?page=2）
        c_page = paginator.page(paginator.num_pages)  # 给最后1页

    # 4. 传数据到模板
    return render(request, 'fee_type.html', {
        'c_page': c_page,
        'paginator': paginator,
        'search_data': search_data,
        "titel":"费用类型"
    })
   

def add_feetype(request):
    if request.method=="GET":
        form=feetypemodel()
        
        return render(request,"add_area.html",{"form":form,"titel":"添加计费类型"})
    form=feetypemodel(data=request.POST)
    if form.is_valid():
        # data=request.session.get('info')
        # if data==None:
        #     return HttpResponse("请先登录")
        # name=data.get('name')
        # logger.info('%s添加了部门'%(name))
        form.save()
        return redirect("/hostel/fee_type/")
    return render(request,"add_area.html",{"form":form,"error":form.errors,"titel":"添加计费类型"})

def del_feetype(request,id):
    row_object=models.feetype.objects.filter(id=id).first()
    if row_object==None:
        return HttpResponse("数据不存在")
    # data=request.session.get('info')
    # if data==None:
    #     return HttpResponse("请先登录")
    # name=data.get('name')
    # logger.info('%s删除了部门数据'%(name))
    row_object.delete()
    return redirect("/hostel/fee_type/")

def edit_feetype(request,id):
    row_object=models.feetype.objects.filter(id=id).first()
    if row_object==None:
        return HttpResponse("要修改的数据不存在")
    if request.method=='GET':
        titel="修改-{}".format(row_object.name)
        form=feetypemodel(instance=row_object)
        return render(request,'add_area.html',{"form":form,"titel":titel})
    form=feetypemodel(data=request.POST,instance=row_object)
    if form.is_valid():
        # data=request.session.get('info')
        # if data==None:
        #     return HttpResponse("请先登录")
        # name=data.get('name')
        # logger.info('%s更新了部门数据'%(name))
        form.save()
        return redirect("/hostel/fee_type/")
    return render(request,'add_area.html',{"form":form,"error":form.errors,"titel":titel})




class fee_recordmodel(BootStrapModelForm):
    class Meta:
        model=models.fee_record_one
        fields="__all__"
    
    
    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get("room")
        date = cleaned_data.get("date")
        power = cleaned_data.get("power")
        water = cleaned_data.get("water")

        # 1. 获取“用量”：从 resource_useage 中查询
        dian_usage_record = models.resource_useage.objects.filter(
            room=room,
            date=date,
            feetype=power
        ).first()
        water_usage_record = models.resource_useage.objects.filter(
            room=room,
            date=date,
            feetype=water
        ).first()
        
        

        # 2. 获取“费用单价”：从 feetype 中获取
        unit_price = feetype.fee
        try:
            unit_price = Decimal(unit_price)
        except DecimalException:
            self.add_error("amount", "费用单价格式错误，请检查计费项目的设置")
            return cleaned_data

        # 3. 计算金额并赋值
        cleaned_data["power"] =round(dian_usage_record.usege * unit_price,2) 
        cleaned_data["water"] =round(water_usage_record.usege * unit_price,2)
        return cleaned_data



def fee_recode(request):#费用细则
    
    search_data = request.GET.get('q', '')
    query = models.fee_record_one.objects.all()
    if search_data:
        query = query.filter(room__room_name__contains=search_data)  # 搜索过滤

    # 2. 分页配置（每页5条）
    paginator = Paginator(query, 5)
    page_num = request.GET.get('page', 1)  # 拿页码，默认1

    # 3. 关键：容错处理（不管页码错成啥样，都返回有效页）
    try:
        c_page = paginator.page(page_num)
           # 尝试拿指定页
    except PageNotAnInteger:  # 页码不是数字（比如?page=abc）
        c_page = paginator.page(1)  # 给第1页
    except EmptyPage:  # 页码超出范围（比如总1页，?page=2）
        c_page = paginator.page(paginator.num_pages)  # 给最后1页
    if paginator.num_pages <= 3:
            page_nums = paginator.page_range  # 所有页码
    else:
            page_nums = [1, 2, 3]

    # 4. 传数据到模板
    return render(request, 'fee_recode.html', {
        'c_page': c_page,
        'paginator': paginator,
        'search_data': search_data,
        "titel":"宿舍缴费记录",
        "page_nums":page_nums,
    })


##增加删除
def add_fee_record(request):
    if request.method=="GET":
        form=fee_recordmodel()
        
        return render(request,"add_area.html",{"form":form,"titel":"添加费用细则"})
    form=fee_recordmodel(data=request.POST)
    if form.is_valid():
        data=request.session.get('info')
        if data==None:
            return HttpResponse("请先登录")
        name=data.get('name')
        logger.info('%s添加了部门'%(name))
        form.save()
        return redirect("/hostel/fee_record/")
    return render(request,"add_area.html",{"form":form,"error":form.errors,"titel":"添加费用细则"})

def del_fee_record(request,id):
    row_object=models.fee_record.objects.filter(id=id).first()
    if row_object==None:
        return HttpResponse("数据不存在")
    data=request.session.get('info')
    if data==None:
        return HttpResponse("请先登录")
    name=data.get('name')
    logger.info('%s删除了宿舍费用记录数据'%(name))
    row_object.delete()
    return redirect("/hostel/fee_record?page={}".format(request.GET.get("page",1)))

#更新和批量添加
def edit_fee_record(request,id):
    row_object=models.fee_record.objects.filter(id=id).first()
    if row_object==None:
        return HttpResponse("要修改的数据不存在")
    if request.method=='GET':
        titel="修改-{}".format(row_object.room)
        form=fee_recordmodel(instance=row_object)
        return render(request,'add_area.html',{"form":form,"titel":titel})
    form=fee_recordmodel(data=request.POST,instance=row_object)
    if form.is_valid():
        # data=request.session.get('info')
        # if data==None:
        #     return HttpResponse("请先登录")
        # name=data.get('name')
        # logger.info('%s更新了部门数据'%(name))
        form.save()
        return redirect("/hostel/fee_record/")
    return render(request,'add_area.html',{"form":form,"error":form.errors,"titel":titel})




#批量上传
def  add_all_fee_record(request):
       
    if request.method == 'GET':
        return render(request, 'add_all_area.html')

    excel_file = request.FILES.get('file')
    if not excel_file:
        return HttpResponse("请选择文件")

    wb = load_workbook(excel_file)
    sheet = wb.active
    errors = []  # 收集错误信息

    # 假设Excel列顺序：
    # row[0] = 用户名（关联Person的name）
    # row[1] = （预留或其他字段，根据实际情况调整）
    # row[2] = 房间名称（关联Room的room_name）
    # row[3] = 入住日期（check_in_date）
    # row[4] = 退房日期（check_out_date）
    # row[5] = 状态（status）

    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            # 1. 解析用户（外键：通过姓名关联Person）
            date = row[0]
            
            if not date:
                errors.append(f"第{idx}行错误：状态为空")
                continue  # 跳行
            date= str(date).strip() 

            # 2. 解析房间（外键：通过房间名称关联Room）
            amount = row[1]
            if not amount:
                errors.append(f"第{idx}行错误：状态为空")
                continue  # 跳行
            amount = str(amount).strip() 

            status = row[2]
            if not status:
                errors.append(f"第{idx}行错误：日期为空")
                continue  # 跳行
            status = str(status).strip() 


            # 3. 解析入住日期（调用辅助函数，处理空值和格式）
            try:
                cdate = parse_date(row[3])
            except ValueError as e:
                errors.append(f"第{idx}行错误：入住日期解析失败 - {str(e)}")
                continue  # 跳行
            check_people = row[4]
            if not check_people:
                errors.append(f"第{idx}行错误：状态为空")
                continue  # 跳行
            check_people = str(check_people).strip()  # 转为字符串并去空格

            room=row[5]
            if not room:
                errors.append(f"第{idx}行错误：状态为空")
                continue  # 跳行
            room=models.Room.objects.filter(id=room).first()
            if not room:
                errors.append(f"第{idx}行错误：房间 '{room}' 不存在")
                continue  # 跳行

           
            models.fee_record.objects.create(
                date=date,
                amount=amount,
                cdate=cdate,
                room=room,
                status=status,
                feetype_id=fee_type,
            )

        except Exception as e:
            errors.append(f"第{idx}行错误：{str(e)}")  # 捕获其他意外错误

    # 处理结果
    if errors:
        return HttpResponse("导入失败：\n" + "\n".join(errors))
    
    logger.info(f"{request.session.get('info', {}).get('name')}批量添加入住记录")
    return redirect('/hostel/fee_record/')
##批量删除
def delete_all_fee_record(request):
    if request.method=="POST":
        
        ids=request.POST.getlist("ids")
        if not ids:
            messages.error(request,"请选择要删除人员")
            return redirect("/hostel/fee_record/")
        try:
            models.fee_record.objects.filter(id__in=ids).delete()##delete少个括号不能删除
            logger.info(f"管理员{request.session.get('info', {}).get('name')}批量删除了记录")
        
            messages.success(request,f"成功删除{len(ids)}条数据")
        except Exception as e:
            messages.error(request,"删除失败")
        return redirect("/hostel/fee_record/")
    if request.method=="GET":
        return redirect("/hostel/fee_record/")

        





class useagemodel(BootStrapModelForm):
    class Meta:
        model = models.resource_useage
        fields = '__all__'



def resource_useage(request):#资源使用量
    search_data = request.GET.get('q', '')
    query = models.resource_useage.objects.all()
    if search_data:
        query = query.filter(room__room_name__contains=search_data)  # 搜索过滤

    # 2. 分页配置（每页5条）
    paginator = Paginator(query, 5)
    page_num = request.GET.get('page', 1)  # 拿页码，默认1

    # 3. 关键：容错处理（不管页码错成啥样，都返回有效页）
    try:
        c_page = paginator.page(page_num)
          # 尝试拿指定页
    except PageNotAnInteger:  # 页码不是数字（比如?page=abc）
        c_page = paginator.page(1)  # 给第1页
    except EmptyPage:  # 页码超出范围（比如总1页，?page=2）
        c_page = paginator.page(paginator.num_pages)  # 给最后1页
    if paginator.num_pages <= 3:
            page_nums = paginator.page_range  # 所有页码
    else:
            page_nums = [1, 2, 3] 

    # 4. 传数据到模板
    return render(request, 'resource_useage.html', {
        'c_page': c_page,
        'paginator': paginator,
        'search_data': search_data,
        "titel":"资源用量记录",
        "page_nums":page_nums,
    })


def add_resource(request):
    if request.method == "GET":
        form = useagemodel()
        return render(request, "add_area.html", {"form": form, "titel": "添加资源用量"})
    form = useagemodel(data=request.POST)
    if form.is_valid():
            form.save()
            return redirect("/hostel/resource_useage/")
    return render(request, "add_area.html", {"form": form, "error": form.errors, "titel": "添加资源用量"})

def del_resource(request, id):
    row_object = models.resource_useage.objects.filter(id=id).first()
    if row_object is None:
            return HttpResponse("数据不存在")
    row_object.delete()
    return redirect("/hostel/resource_useage/")

def edit_resource(request, id):
    row_object = models.resource_useage.objects.filter(id=id).first()
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




def add_all_resource(request):
    if request.method == 'GET':
        return render(request, 'add_all_area.html')

    excel_file = request.FILES.get('file')
    if not excel_file:
        return HttpResponse("请选择文件")

    wb = load_workbook(excel_file)
    sheet = wb.active
    errors = []  # 收集错误信息

    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            # 1. 解析房间（外键：room）
            room_name = row[0]
            if not room_name:
                errors.append(f"第{idx}行错误：房间号为空，无法关联")
                continue
            room = models.Room.objects.filter(room_name=room_name).first()
            if not room:
                errors.append(f"第{idx}行错误：房间 '{room_name}' 不存在")
                continue

            # 2. 解析计费类型（外键：feetype）
            feetype_name = row[3]
            if not feetype_name:
                errors.append(f"第{idx}行错误：计费类型为空")
                continue
            feetype = models.feetype.objects.filter(name=feetype_name).first()
            if not feetype:
                errors.append(f"第{idx}行错误：计费类型 '{feetype_name}' 不存在")
                continue

            # 3. 解析计算月份（date，字符串类型）
            date = row[1]
            if not date:
                errors.append(f"第{idx}行错误：计算月份为空")
                continue
            date = str(date).strip()

            # 4. 解析用量（usege，Decimal类型）
            usege = row[2]
            if not usege:
                usege = None  # 模型允许空值，空时设为None
            else:
                usege = float(usege)  # 转为浮点数，兼容DecimalField

            # 5. 解析录入日期（check_in_date，日期类型）
            try:
                check_in_date = parse_date(row[4])
            except ValueError as e:
                errors.append(f"第{idx}行错误：录入日期解析失败 - {str(e)}")
                continue

            # 6. 解析录入人（check_people）
            check_people = row[5]
            if not check_people:
                errors.append(f"第{idx}行错误：录入人为空")
                continue
            check_people = str(check_people).strip()

            # 7. 创建资源使用记录（严格对齐模型字段名！）
            models.resource_useage.objects.create(
                room=room,
                feetype=feetype,
                date=date,
                usege=usege,
                check_in_date=check_in_date,
                check_people=check_people
            )

        except Exception as e:
            errors.append(f"第{idx}行错误：{str(e)}")

    if errors:
        return HttpResponse("导入失败：\n" + "\n".join(errors))
    
    logger.info(f"{request.session.get('info', {}).get('name')}批量添加资源使用记录")
    return redirect('/hostel/resource_useage/')

from django.contrib import messages
##资源使用批量删除
def delete_all_resource(request):
    if request.method == 'POST':
        # 获取勾选的person ID列表（前端表单name为"ids"）
        ids = request.POST.getlist('ids')
        if not ids:
            messages.error(request, "请选择要删除的人员")
            return redirect('/hostel/resource_useage/')
        
        try:
            # 批量删除选中的记录
            models.resource_useage.objects.filter(id__in=ids).delete()
            messages.success(request, f"成功删除 {len(ids)} 条人员记录")
            logger.info(f"管理员{request.session.get('info', {} ).get('name')}删除了{len(ids)}条资源用量记录")
        except Exception as e:
            messages.error(request, f"删除失败：{str(e)}")
        
        return redirect('/hostel/resource_useage/')
    
    # 非POST请求直接跳转回列表页
    return redirect('/hostel/resource_useage/')






   

class standardmodel(BootStrapModelForm):
    class Meta:
        model=models.standard
        fields="__all__"

def standard(request):#计费标准
    search_data = request.GET.get('q', '')
    query = models.standard.objects.all()
    if search_data:
        query = query.filter(name__contains=search_data)  # 搜索过滤

    # 2. 分页配置（每页5条）
    paginator = Paginator(query, 5)
    page_num = request.GET.get('page', 1)  # 拿页码，默认1

    # 3. 关键：容错处理（不管页码错成啥样，都返回有效页）
    try:
        c_page = paginator.page(page_num)  # 尝试拿指定页
    except PageNotAnInteger:  # 页码不是数字（比如?page=abc）
        c_page = paginator.page(1)  # 给第1页
    except EmptyPage:  # 页码超出范围（比如总1页，?page=2）
        c_page = paginator.page(paginator.num_pages)  # 给最后1页

    # 4. 传数据到模板
    return render(request, 'standard.html', {
        'c_page': c_page,
        'paginator': paginator,
        'search_data': search_data,
        "titel":"计费标准"
    })

def add_standard(request):
        if request.method == "GET":
            form = standardmodel()
            return render(request, "add_area.html", {"form": form, "titel": "添加计费标准"})
        form = standardmodel(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("/hostel/standard/")
        return render(request, "add_area.html", {"form": form, "error": form.errors, "titel": "添加计费标准"})

def del_standard(request, id):
        row_object = models.standard.objects.filter(id=id).first()
        if row_object is None:
            return HttpResponse("数据不存在")
        row_object.delete()
        return redirect("/hostel/standard/")

def edit_standard(request, id):
        row_object = models.standard.objects.filter(id=id).first()
        if row_object is None:
            return HttpResponse("要修改的数据不存在")
        if request.method == 'GET':
            titel = "修改-{}".format(row_object.room)
            form = standardmodel(instance=row_object)
            return render(request, 'add_area.html', {"form": form, "titel": titel})
        form = standardmodel(data=request.POST, instance=row_object)
        if form.is_valid():
            form.save()
            return redirect("/hostel/standard/")
        return render(request, 'add_area.html', {"form": form, "error": form.errors, "titel": titel})

class feesharingmodel(BootStrapModelForm):
    class Meta:
        model=models.feesharing
        fields=["occupancyrecord","fee_type","fee_record","feesharings","status","start_date","end_date"]
        

    def clean(self):
        # 修正拼写：fee_record（原fee_recode是错的）
        fee_record = self.cleaned_data.get("fee_record")  
        if fee_record:
            total_amount = fee_record.amount
            print("total_amount:", total_amount)
            room = fee_record.room
            room_people = room.people
            print("room_people:", room_people)
            if room_people > 0:
                sharing_amount = round(total_amount / room_people,2)
                print("sharing_amount:", sharing_amount)
                self.cleaned_data["feesharings"] = sharing_amount
                print(self.cleaned_data["feesharings"])
            else:
                self.add_error("feesharings", "房间人数为0,无法计算分摊")
                print("Error: 房间人数为0,无法计算分摊")
        return self.cleaned_data




    
def feesharing(request):#feesharing费用分摊
    search_data = request.GET.get('q', '')
    query = models.feesharing.objects.all()
    if search_data:
        query = query.filter(occpancyrecord__user__contains=search_data)  # 搜索过滤

    # 2. 分页配置（每页5条）
    paginator = Paginator(query, 5)
    page_num = request.GET.get('page', 1)  # 拿页码，默认1

    # 3. 关键：容错处理（不管页码错成啥样，都返回有效页）
    try:
        c_page = paginator.page(page_num)
        if paginator.num_pages <= 3:
            page_nums = paginator.page_range  # 所有页码
        else:
            page_nums = [1, 2, 3]   # 尝试拿指定页
    except PageNotAnInteger:  # 页码不是数字（比如?page=abc）
        c_page = paginator.page(1)  # 给第1页
    except EmptyPage:  # 页码超出范围（比如总1页，?page=2）
        c_page = paginator.page(paginator.num_pages)  # 给最后1页
    if paginator.num_pages <= 3:
            page_nums = paginator.page_range  # 所有页码
    else:
            page_nums = [1, 2, 3]

    # 4. 传数据到模板
    return render(request, 'feesharing.html', {
        'c_page': c_page,
        'paginator': paginator,
        'search_data': search_data,
        "titel":"费用分摊记录",
        "page_nums":page_nums,
    })
   
def add_feesharing(request):
    fee_records = models.fee_record.objects.all().order_by('-id')
    if request.method=="GET":
        form=feesharingmodel()
        return render(request,"add_area.html",{"form":form,"titel":"添加分摊记录","fee_records":fee_records})
    form=feesharingmodel(data=request.POST)
    if form.is_valid():
        # data=request.session.get('info')
        # if data==None:
        #     return HttpResponse("请先登录")
        # name=data.get('name')
        # logger.info('%s添加了部门'%(name))
        form.save()
        return redirect("/hostel/feesharing/")
    return render(request,"add_area.html",{"form":form,"error":form.errors,"titel":"添加分摊记录","fee_records":fee_records})

def del_feesharing(request,id):
    row_object=models.feesharing.objects.filter(id=id).first()
    if row_object==None:
        return HttpResponse("数据不存在")
    # data=request.session.get('info')
    # if data==None:
    #     return HttpResponse("请先登录")
    # name=data.get('name')
    # logger.info('%s删除了部门数据'%(name))
    row_object.delete()
    return redirect("/hostel/feesharing/?page={}".format(request.GET.get("page",1)))

def edit_feesharing(request,id):
    row_object=models.feesharing.objects.filter(id=id).first()
    if row_object==None:
        return HttpResponse("要修改的数据不存在")
    if request.method=='GET':
        titel="修改-{}".format(row_object.occupancyrecord)
        form=feesharingmodel(instance=row_object)
        return render(request,'add_area.html',{"form":form,"titel":titel})
    form=feesharingmodel(data=request.POST,instance=row_object)
    if form.is_valid():
        # data=request.session.get('info')
        # if data==None:
        #     return HttpResponse("请先登录")
        # name=data.get('name')
        # logger.info('%s更新了部门数据'%(name))
        form.save()
        return redirect("/hostel/feesharing/")
    return render(request,'add_area.html',{"form":form,"error":form.errors,"titel":titel})

##批量上传
def add_all_feesharing(request):
    if request.method == 'GET':
        return render(request, 'add_all_area.html')

    excel_file = request.FILES.get('file')
    if not excel_file:
        return HttpResponse("请选择文件")

    wb = load_workbook(excel_file)
    sheet = wb.active
    errors = []

    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            # 1. 解析费用细则（外键：fee_record）
            fee_record_name = row[0]
            if not fee_record_name:
                errors.append(f"第{idx}行错误：费用细则为空")
                continue
            fee_record = models.fee_record.objects.filter(name=fee_record_name).first()
            if not fee_record:
                errors.append(f"第{idx}行错误：费用细则 '{fee_record_name}' 不存在")
                continue

            # 2. 解析计费类型（外键：feetype）
            feetype_name = row[1]
            if not feetype_name:
                errors.append(f"第{idx}行错误：计费类型为空")
                continue
            feetype = models.feetype.objects.filter(name=feetype_name).first()
            if not feetype:
                errors.append(f"第{idx}行错误：计费类型 '{feetype_name}' 不存在")
                continue

            # 3. 解析住宿记录（外键：occupancyrecord）
            occupancyrecord_name = row[2]
            if not occupancyrecord_name:
                errors.append(f"第{idx}行错误：住宿记录为空")
                continue
            occupancyrecord = models.occupancyrecord.objects.filter(name=occupancyrecord_name).first()
            if not occupancyrecord:
                errors.append(f"第{idx}行错误：住宿记录 '{occupancyrecord_name}' 不存在")
                continue

            # 4. 解析个人分摊金额
            feesharing_amount = row[3]
            if not feesharing_amount:
                errors.append(f"第{idx}行错误：个人分摊金额为空")
                continue
            feesharing_amount = str(feesharing_amount).strip()

            # 5. 解析是否缴纳（状态）
            status = row[4]
            if status not in ['0', '1']:
                errors.append(f"第{idx}行错误：是否缴纳状态必须为 '0' 或 '1'，当前值为 '{status}'")
                continue

            # 6. 解析开始计费日期
            start_date = parse_date(row[5])
            if not start_date:
                errors.append(f"第{idx}行错误：开始计费日期格式错误（需为 YYYY-MM-DD）")
                continue

            # 7. 解析结束计费日期
            end_date = parse_date(row[6])
            if not end_date:
                errors.append(f"第{idx}行错误：结束计费日期格式错误（需为 YYYY-MM-DD）")
                continue

            # 8. 解析缴纳时间（可为空）
            pay_date = parse_date(row[7]) if row[7] else None

            # 9. 创建费用分摊记录
            models.feesharing.objects.create(
                fee_record=fee_record,
                fee_type=feetype,
                occupancyrecord=occupancyrecord,
                feesharing=feesharing_amount,
                status=status,
                start_date=start_date,
                end_date=end_date,
                date=pay_date
            )

        except Exception as e:
            errors.append(f"第{idx}行错误：{str(e)}")

    if errors:
        return HttpResponse("导入失败：\n" + "\n".join(errors))
    
    logger.info(f"{request.session.get('info', {}).get('name')}批量添加费用分摊记录")
    messages.success(request, "批量导入成功！")
    return redirect('/hostel/feesharing/')


def del_all_feesharing(request):#批量删除
    if request.method=="POST":
        ids=request.POST.getlist("ids")
        if not ids:
            messages.error(request,"请选择要删除的对象")
        try:
            models.feesharing.objects.filter(id_in=ids).delete()
            messages.success(request,f"成功删除{len(ids)}条数据")
            logger.info(f"管理员{request.session.get('info', {} ).get('name')}删除了{len(ids)}条分摊记录")
        except Exception as e:
            messages.error(request,'删除失败')
        return redirect("/hostel/feesharing/")
    return redirect("/hostel/feesharing/")






