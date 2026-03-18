from django.apps import AppConfig


class HostelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hostel'
    
    # def ready(self):
    #     import hostel.signals  # 导入上面写的信号文件
