"""
B站登录应用

提供B站扫码登录功能，包括：
1. 检查登录状态
2. 生成登录二维码
3. 轮询扫码状态
4. 保存登录cookie
"""

default_app_config = 'bilibili_login.apps.BilibiliLoginConfig'
