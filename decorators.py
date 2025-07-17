from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from .utils import BilibiliLogin

def bilibili_login_required(view_func):
    """
    检查B站登录状态的装饰器，如果未登录或登录已过期，则重定向到登录页面
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 检查cookie是否过期
        if BilibiliLogin.check_cookie_expired():
            # 如果是AJAX请求，返回JSON响应
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'B站登录已过期，请重新登录',
                    'redirect_url': reverse('bilibili_login:login_qrcode')
                }, status=401)
            # 否则重定向到登录页面
            return redirect('bilibili_login:login_qrcode')
        
        # 如果已登录，则继续执行视图函数
        return view_func(request, *args, **kwargs)
    
    return wrapper 