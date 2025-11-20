
from django.core.paginator import Paginator
from django.shortcuts import render
from . import models
from hostel import models
from hostel.models import area ,dorm
#count:count需要分页的对象总数,分页对象记录总数
#num_pages:分页后的页面总数
#page_range:从一开始的range对象,记录页码的循环范围
# per_page=10#每页显示10条记录
# page_num=request.GET.get("page",1)#获取当前的页码,没有默认为1
#c_page.num代表当前正在显示的那一页
 # num是实例的属性,用于获取当前页码的数字

# page=Paginator.page()

# Paginator

def test_page(request):
     page_num=request.GET.get("page",1)
     all_data=models.area.objects.all()
     paginator=Paginator(all_data,5)
     
     c_page=paginator.page(page_num)
     return render(request,'area.html', {'c_page': c_page, 'paginator': paginator})
