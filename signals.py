from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings

from .utils import BilibiliLogin

@receiver(post_migrate)
def check_bilibili_login(sender, **kwargs):
    """
    在Django应用启动时检查B站登录状态
    如果需要自动启动登录流程，可以在这里添加相关代码
    """
    # 仅在开发环境下自动检查登录状态
    if settings.DEBUG:
        print("检查B站登录状态...")
        if BilibiliLogin.check_cookie_expired():
            print("B站登录已过期，请运行 python manage.py check_bilibili_login 命令进行登录")
        else:
            print("B站登录状态有效") 