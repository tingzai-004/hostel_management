from django.contrib import admin
from django.utils.html import format_html
from .models import occupancyrecord  # ← 重点！导入您的住宿记录模型

@admin.register(occupancyrecord)
class OccupancyRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'check_in_date', 'check_out_date', 'discount_status', 'status']
    list_filter = ['status', 'discount']  # 右边还能按是否优惠筛选
    search_fields = ['user__name', 'room__room_name']  # 能搜名字和房间

    # 这就是魔法！把 True/False 变成好看文字+颜色
    def discount_status(self, obj):
        if obj.discount:
            return format_html('<b style="color:green;">已优惠</b>')
        else:
            return format_html('<b style="color:orange;">无优惠</b>')
    discount_status.short_description = "优惠"
    
    # 给这列起个好听的名字
    