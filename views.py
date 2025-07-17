from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import time
import threading
import json

from .utils import BilibiliLogin

def check_login_status(request):
    """检查B站登录状态"""
    is_expired = BilibiliLogin.check_cookie_expired()
    return JsonResponse({
        'is_expired': is_expired,
        'message': '登录已过期，请重新登录' if is_expired else '登录状态有效'
    })

def login_qrcode(request):
    """生成B站登录二维码"""
    # 申请二维码
    qrcode_key, qrcode_url, error = BilibiliLogin.generate_qrcode()
    
    if error:
        return JsonResponse({'success': False, 'message': error})
    
    # 生成二维码并在浏览器中显示
    BilibiliLogin.show_qrcode_in_browser(qrcode_url)
    
    # 启动一个线程轮询扫码状态
    polling_thread = threading.Thread(target=poll_login_status, args=(qrcode_key,))
    polling_thread.daemon = True
    polling_thread.start()
    
    return JsonResponse({
        'success': True, 
        'message': '二维码已生成，请使用B站App扫描',
        'qrcode_key': qrcode_key
    })

def poll_login_status(qrcode_key):
    """轮询扫码状态"""
    max_attempts = 60  # 最多尝试60次，每次3秒，共3分钟
    attempt = 0
    
    while attempt < max_attempts:
        # 查询扫码状态
        scan_code, cookies, message = BilibiliLogin.poll_qrcode_status(qrcode_key)
        
        # 打印扫码状态
        print(f"扫码状态: {scan_code}, {message}")
        
        # 根据扫码状态处理
        if scan_code == BilibiliLogin.STATUS_SUCCESS:
            # 登录成功，保存cookie
            if cookies and BilibiliLogin.save_cookies(cookies):
                print("登录成功，cookie已保存")
            else:
                print("登录成功，但cookie保存失败")
            break
        elif scan_code == BilibiliLogin.STATUS_QR_EXPIRED:
            # 二维码已过期
            print("二维码已过期，请重新获取")
            break
        elif scan_code == BilibiliLogin.STATUS_SCANNED_NOT_CONFIRMED:
            # 已扫描未确认，继续等待
            print("二维码已扫描，等待确认")
        
        # 等待3秒后再次查询
        time.sleep(3)
        attempt += 1
    
    if attempt >= max_attempts:
        print("二维码扫描超时，请重新获取")

@require_http_methods(["GET"])
def login_status(request):
    """获取登录状态"""
    qrcode_key = request.GET.get('qrcode_key')
    
    if not qrcode_key:
        return JsonResponse({'success': False, 'message': '缺少qrcode_key参数'})
    
    # 查询扫码状态
    scan_code, cookies, message = BilibiliLogin.poll_qrcode_status(qrcode_key)
    
    # 根据扫码状态返回结果
    if scan_code == BilibiliLogin.STATUS_SUCCESS:
        # 登录成功，保存cookie
        if cookies and BilibiliLogin.save_cookies(cookies):
            return JsonResponse({'success': True, 'status': 'success', 'message': '登录成功'})
        else:
            return JsonResponse({'success': False, 'status': 'error', 'message': 'Cookie保存失败'})
    elif scan_code == BilibiliLogin.STATUS_QR_EXPIRED:
        return JsonResponse({'success': False, 'status': 'expired', 'message': '二维码已过期'})
    elif scan_code == BilibiliLogin.STATUS_SCANNED_NOT_CONFIRMED:
        return JsonResponse({'success': True, 'status': 'waiting_confirm', 'message': '已扫描，等待确认'})
    elif scan_code == BilibiliLogin.STATUS_NOT_SCANNED:
        return JsonResponse({'success': True, 'status': 'waiting_scan', 'message': '等待扫描'})
    else:
        return JsonResponse({'success': False, 'status': 'error', 'message': f'未知状态: {message}'})
