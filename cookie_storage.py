import json
import os
import time
from pathlib import Path
from django.conf import settings

# 定义cookie文件的路径
COOKIE_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / 'data' / 'bilibili_cookie.json'

# 确保目录存在
os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)

# 默认cookie结构
DEFAULT_COOKIE = {
    'DedeUserID': '',
    'DedeUserID__ckMd5': '',
    'Expires': '0',
    'SESSDATA': '',
    'bili_jct': '',
    'gourl': 'https%3A%2F%2Fwww.bilibili.com',
    'first_domain': '.bilibili.com'
}


def load_cookie():
    """
    加载B站cookie
    """
    try:
        if os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载cookie异常: {str(e)}")
        return DEFAULT_COOKIE


def save_cookie(cookie_dict):
    """
    保存B站cookie
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
        
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookie_dict, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存cookie异常: {str(e)}")
        return False


def check_cookie_expired():
    """
    检查B站cookie是否过期
    """
    try:
        # 获取当前时间戳
        current_timestamp = int(time.time())
        
        # 加载cookie
        cookie = load_cookie()
        
        # 获取cookie中的过期时间
        expires_timestamp = int(cookie.get('Expires', 0))
        
        # 如果过期时间小于当前时间，或者没有过期时间，则认为已过期
        return expires_timestamp <= current_timestamp or expires_timestamp == 0
    except (ValueError, AttributeError, TypeError):
        # 如果出现任何异常，则认为已过期
        return True


def get_cookie():
    """
    获取B站cookie
    """
    return load_cookie() 