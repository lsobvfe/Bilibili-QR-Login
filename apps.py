from django.apps import AppConfig


class BilibiliLoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bilibili_login'
    verbose_name = 'B站登录'
    
    def ready(self):
        """应用启动时执行的初始化操作"""
        # 导入信号处理器
        import bilibili_login.signals
