"""
URL configuration for management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from hostel import views,person,paginator,fee,login,status,part,print,a,b,admin_list,user2,check_out,room_type,discount,resourece
from hostel import hostel_assert
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
# from hostel.views import AreaBulkDeleteView

 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hostel/area/',views.area),
    path('hostel/add_area/',views.add_area),
    path('hostel/delete_area/<int:id>/',views.delete_area),
    path('hostel/edit_area/<int:id>/',views.edit_area),
    path('hostel/add_all_area/',views.add_all_area),
    path("hostel/delete_all_area/",views.delete_all_area),
  
    #楼栋
    path('hostel/dorm/',views.dorm),
    path('hostel/add_dorm/',views.add_dorm),
    path('hostel/delete_dorm/<int:id>/',views.delete_dorm),
    path('hostel/edit_dorm/<int:id>/',views.edit_dorm),
    path('hostel/add_all_dorm/',views.add_all_dorm),
    path('hostel/delete_all_dorm/',views.delete_all_dorm),

    ##房间
    path('hostel/room/',views.room),
    path('hostel/add_room/',views.add_room),
    path('hostel/delete_room/<int:id>/',views.delete_room),
    path('hostel/edit_room/<int:id>/',views.edit_room),
    path('hostel/add_all_room/',views.add_all_room),
    path('hostel/delete__all_room/',views.delete_all_room),
   
    ###人员
    path('hostel/person/',person.person),
    path('hostel/add_person/',person.add_person),
    # path('person/delete/<int:pk>/', person.PersonDeleteView.as_view(), name='person_delete'),
    path('hostel/edit_person/<int:id>/',person.edit_person),
    path('hostel/add_all_person/',person.add_all_person),
    path('hostel/delete_all_person/',person.delete_all_person),
    path("hostel/delete_person/<int:id>/",person.delete_person),
    ###住宿记录
    path('hostel/occupancyrecord/',person.occupancyrecord),
    path('hostel/add_occupancyrecord/',person.add_occupancyrecord), 
    path('hostel/delete_occupancyrecord/<int:id>/',person.delete_occupancyrecord),
    path('hostel/edit_occupancyrecord/<int:id>/',person.edit_occupancyrecord),
    path('hostel/add_all_occupancyrecord/',person.add_all_occupancyrecord),
    path('hostel/delete_all_occupancyrecord/',person.delete_all_occupancyrecord),
    ##退宿记录
    path('hostel/checkout_occupancyrecord/<int:id>/',check_out.checkout_occupancyrecord),
    path('hostel/checkout_record/',check_out.checkout_record),
    path('hostel/delete_checkout/<int:id>/',check_out.delete_checkout),
    path('hostel/edit_checkout/<int:id>/',check_out.edit_checkout),
    ##部门
    path('hostel/dep/',person.dep),
    path('hostel/add_dep/',person.add_dep),
    path('hostel/delete_dep/<int:id>/',person.delete_dep),
    path('hostel/edit_dep/<int:id>/',person.edit_dep),
    #用户类型
    path('hostel/user_type/',person.user_type),
    path('hostel/add_usertype/',person.add_user_type),
    path('hostel/delete_type/<int:id>/',person.del_type),
    path('hostel/update_type/<int:id>/',person.update_type),
    #权限
    path('hostel/permission/',person.permission),
    path('test_page/',paginator.test_page),
    path('hostel/add_permission/',person.add_permission),
    path('hostel/del_permission/<int:id>/',person.del_permission),
    path('hostel/edit_permission/<int:id>/',person.edit_permission),

    ##费用类型
    path('hostel/fee_type/',fee.fee_type),
    path('hostel/add_feetype/',fee.add_feetype),
    path('hostel/delete_feetype/<int:id>/',fee.del_feetype),
    path('hostel/edit_feetype/<int:id>/',fee.edit_feetype),   
     
    #费用分摊
    path('hostel/feesharing/',fee.sharing),
    path("hostel/del_all_feesharing/",fee.del_all_feesharing),
  
    path('hostel/add_all_feesharing/',fee.add_all_feesharing),
    # path('hostel/add_feesharing/',fee.add_feesharing),
    path('hostel/edit_feesharing/<int:id>/',fee.edit_feesharing),
    path('hostel/del_feesharing/<int:id>/',fee.del_feesharing),
   
    #费用细则
    path('hostel/fee_record/',fee.fee_recode),
    path('hostel/add_fee_record/',fee.add_fee_record),
    path('hostel/del_fee_record/<int:id>/',fee.del_fee_record),
    path('hostel/edit_fee_record/<int:id>/',fee.edit_fee_record),
    path("hostel/add_all_fee_record/",fee.add_all_fee_record),
    path("hostel/delete_all_fee_record/",fee.delete_all_fee_record),
   


    #资源使用量
    path("hostel/resource_useage/",resourece.resource_useage_list),
    path("hostel/add_resource/",resourece.add_resource),
    path("hostel/del_resource/<int:id>/",resourece.del_resource),
    path("hostel/edit_resource/<int:id>/",resourece.edit_resource),
    # path('hostel/add_all_resource/',resourece.add_all_resource),
    # path('hostel/delete_all_resource/',resourece.delete_all_resource),

    #登录
    path('login/',login.admin_login,name="login"),
    #modelform
    path("hostel/modelform/",login.upload),
    path("hostel/statusUI/",login.statuUI),
    path("hostel/logo/",login.bg),
    path('logout/',login.logout),
    #重置
    path("hostel/admin_reset/",part.admin_reset),
    #报表
    path("table/",part.table),
    path("table2/",part.table2),
    
    # path('areas/bulk-delete/', AreaBulkDeleteView.as_view(), name='area_bulk_delete'),

    path("statusUI/",status.statusUI,name="statusUI"),
    ##
    path("peint/",part.peint),
    path("peint2/",print.peint2),
    path("peint3/",print.peint),
    ##
    path("upload_back/",a.upload_back),
    ##个人中心
    # path("upload_a_img/",b.upload_a_img),
    # path("user_img/",b.user_img),
    ##管理员liebiao
    path("admin_list/",admin_list.admin_list),
    path('add_admin/',admin_list.add_admin),
    path('delete_admin/<int:id>/',admin_list.delete_admin),
    path('editor_admin/<int:id>/',admin_list.editor_admin),
    ##yhu
    path("user/login/",user2.user_login,name="user_login"),
    path('miao/',user2.miao),
    path("user/logout/",user2.logout),
    path("user/reset/",user2.user_reset),
    path("add_money/",a.money_upload),
    ##房型
    path('add_room_type/', room_type.add_room_type, name='room_type_view'),
    path('hostel/room_type/',room_type.room_type),
    path('hostel/delete_room_type/<int:id>/',room_type.delete_room_type),
    path('hostel/delete_all_room_type/',room_type.delete_all_room_type),
    path('hostel/edit_room_type/<int:id>/',room_type.edit_room_type),
    ##折扣
    path('hostel/discount/',discount.discount_views),
    path('hostel/delete_discount/<int:id>/',discount.delete_discount),
    path('hostel/edit_discount/<int:id>/',discount.edit_discount),
    path('hostel/add_discount/',discount.add_discount),
    path('hostel/del_all_discount/',discount.del_all_discount),
    ##资产类别
    path('hostel/assetcategory/',hostel_assert.assetcategory_view),
    path('hostel/add_assetcategory/',hostel_assert.add_assetcategory),
    path('hostel/delete_assetcategory/<int:id>/',hostel_assert.delete_assetcategory),
    path('hostel/edit_assetcategory/<int:id>/',hostel_assert.edit_assetcategory),
    path('hostel/delete_all_assetcategory/',hostel_assert.del_all_assetcategory),
    ##资产
    path('hostel/asset/',hostel_assert.asset),
    path('hostel/asset_create/',hostel_assert.asset_create),
    path('hostel/asset_update/<int:id>/',hostel_assert.asset_update),
    ##资产详情
    path('hostel/assetchill/<int:id>/',hostel_assert.assetchill,name='asset'),
    path('hostel/delete_assetchill/<int:id>/',hostel_assert.delete_assetchill,name='delete_asset'),
    path('hostel/edit_assetchill/<int:id>/',hostel_assert.edit_assetchill,name='edit_asset'),



    
    

    #media配置
     re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT},name='media'),
     path('status/',views.status)
]

        
    

