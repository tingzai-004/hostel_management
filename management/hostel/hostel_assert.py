from django.shortcuts import render,HttpResponse,redirect
from . import models
from hostel import models
from hostel.models import Asset,AssetCategory
from django import forms
from openpyxl import load_workbook
from hostel.bootstrap import BootStrapModelForm
import logging
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
import io
from django.contrib import messages
from django.db.models import Count,Sum
from django.db.models.functions import Coalesce
from django.db.models import Sum, DecimalField
logger=logging.getLogger('management')

def assetcategory_view(request):
    search_data=request.GET.get('q','')
    query=models.AssetCategory.objects.all().order_by('id')
    if  search_data:
        query=query.filter(name__contains=search_data)
    page_num=request.GET.get('page',1)
    paginator=Paginator(query,5)
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
        'search_data':search_data,
        'paginator':paginator,
        'page_nums':page_nums
    }
    return render(request,'assetcategory.html',context)

class addassetcategory(BootStrapModelForm):
    class Meta:
        model=AssetCategory
        fields="__all__"
    
def add_assetcategory(request):
    if request.method=="GET":
        form=addassetcategory()
        return render(request,'add_asset.html',{'form':form})
    form=addassetcategory(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/hostel/assetcategory/')
    return render(request,'add_asset.html',{'form':form})

def delete_assetcategory(request,id):
    page_nums=request.GET.get('page',1)
    page_nums=int(page_nums)
    row_obj=models.AssetCategory.objects.filter(id=id).first()
    if not row_obj:
        messages.error(request,"找不到数据")
        return redirect(f'/hostel/assetcategory?page={page_nums}')
    try:
        row_obj.delete()
        messages.info(request,"成功删除一条财产类型记录")
        logger.info(f"{request.session.get('info',{}).get('name')}删除了一条财产类型记录")
        return redirect(f'/hostel/assetcategory?page={page_nums}')
    except Exception as e:
        messages.error(request,"删除失败")

def edit_assetcategory(request,id):
    page_nums=request.GET.get('page',1)
    page_nums=int(page_nums)
    row_obj=models.AssetCategory.objects.filter(id=id).first()
    titel="编辑-{}的信息".format(row_obj.name)
    if row_obj:
        if request.method=="GET":
            form=addassetcategory(instance=row_obj)
            return render(request,'add_area.html',{'form':form,'titel':titel})
        form=addassetcategory(data=request.POST,instance=row_obj)
        if form.is_valid():
            form.save()
            return redirect(f'/hostel/assetcategory?page={page_nums}')
        return render(request,'add_area.html',{'form':form,'titel':titel})
    else:
        messages.error(request,'无数据')

def del_all_assetcategory(request):
    if request.method=='POST':
        ids=request.POST.getlist('ids')
        if not ids:
            messages.error(request,'请选择数据')
            return redirect('/hostel/assetcategory/')
        try:
            models.AssetCategory.objects.filter(id__in=ids).delete()
            messages.info(request,f"管理成功删除了{len(ids)}条数据")
        except Exception as e:
            messages.error(request,f"删除失败{str(e)}")
        return redirect ("/hostel/assetcategory/")
    return redirect('/hostel/assetcategory/')


######

def asset(request):
    page_num=request.GET.get('page',1)
    
    room_num=models.Room.objects.count()
    asset_num=models.Asset.objects.count()
    rooms=models.Room.objects.prefetch_related('assets__category').annotate(total=Count('assets'))
    paginator=Paginator(rooms,4)
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
    for room in c_page:
        stats = {}  # 用来记录分类统计，比如：{'空调': 2, '桌子': 1}
    
        for asset in room.assets.all():  # 遍历这个房间的所有资产
            cat_name = asset.category.name  # 获取资产分类名称
        # 统计数量：如果已有这个分类就+1，没有就设为1
            stats[cat_name] = stats.get(cat_name, 0) + 1
    
    # 把统计结果转换成方便模板使用的格式
        room.category_stats = [{'name': name, 'count': count} for name, count in stats.items()]
    return render(request,'asset.html',{'rooms':rooms,'room_num':room_num,'asset_num':asset_num,'paginator':paginator,'c_page':c_page,'page_nums':page_nums})

from django import forms
from .models import Asset

class AssetModelForm(forms.ModelForm):
    class Meta:
        model = Asset
        # 自动包含所有字段（也可以指定需要的字段）
        fields = '__all__'
        # 自定义控件和提示（可选）
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'bound_at': forms.DateInput(attrs={'type': 'date'}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'status': forms.Select(choices=[
                ('normal', '正常'),
                ('repair', '维修中'),
                ('discard', '已报废'),
            ]),
        }
        # 字段提示文本（可选）
        help_texts = {
            'asset_code': '资产唯一编码(例如:AC2501)',
            'price': '单位：元，保留两位小数',
        }

    # 自定义验证（可选）
    def clean_asset_code(self):
        asset_code = self.cleaned_data.get('asset_code')
        # 编辑时排除当前实例，避免重复
        if Asset.objects.filter(asset_code=asset_code).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError('该资产编码已存在，请更换')
        return asset_code
    
from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset


# 添加资产
def asset_create(request):
    if request.method == 'POST':
        form = AssetModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/hostel/asset/')  # 跳转回资产列表页
    else:
        form = AssetModelForm()  # GET 请求显示空表单
    return render(request, 'assetmodel.html', {'form': form})

# 编辑资产（接收资产ID）
def asset_update(request, id):
    asset = get_object_or_404(Asset, id=id)
    if request.method == 'POST':
        form = AssetModelForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('/hostel/asset/')
    else:
        form = AssetModelForm(instance=asset)  # 加载现有数据
    return render(request, 'assetmodel.html', {'form': form})


def assetchill(request,id):
    room=models.Room.objects.filter(id=id).first()
    dorm=room.dorm
    room_type=room.room_type
    assets=room.assets.all().count()
    
    asset=room.assets.all()
    asset_sum = asset.aggregate(
    total=Sum('price', output_field=DecimalField())
)['total'] or 0
    return render(request,'assetchill.html',{"dorm":dorm,"room_type":room_type,"room":room,"assets":assets,"asset":asset,"asset_sum":asset_sum})

def delete_assetchill(request,id):
    row_obj=models.Asset.objects.filter(id=id).first()
    room_id=row_obj.room.id
    if not row_obj:
        messages.error(request,"数据不存在")
        return redirect('asset',id=room_id)
    try:
        logger.info(f"{request.session.get('info',{}).get('name')}删除了{row_obj.name}的信息")
        row_obj.delete()
        
    except Exception as e:
        messages.error(request,"删除失败")
    return redirect('asset',id=room_id)

class AsseteditModelForm(forms.ModelForm):
    class Meta:
        model = Asset
        # 自动包含所有字段（也可以指定需要的字段）
        fields = ['price','name','model','brand','status']
        # 自定义控件和提示（可选）
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'bound_at': forms.DateInput(attrs={'type': 'date'}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'status': forms.Select(choices=[
                ('normal', '正常'),
                ('repair', '维修中'),
                ('discard', '已报废'),
            ]),
        }

def edit_assetchill(request,id):
    row_obj=models.Asset.objects.filter(id=id).first()
    room_id=row_obj.room.id
    title='编辑-{}的信息'.format(row_obj.name)
    if not row_obj:
        messages.error(request,"数据不存在")
        return redirect('asset',id=room_id)
    if request.method=="GET":
        form=AsseteditModelForm(instance=row_obj)
        return render(request,"edit_asset.html",{'form':form,'title':title})
    form=AsseteditModelForm(data=request.POST,instance=row_obj)
    if form.is_valid():
        logger.info(f"{request.session.get('info',{}).get('name')}编辑了{row_obj.name}的信息")
        form.save()
        return redirect('asset',id=room_id)
    return render(request,"edit_asset.html",{'form':form,'title':title})
        
    


    





            






    
        
    
    


