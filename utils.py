import requests
import time
import os
import qrcode
from PIL import Image
import base64
import io
import webbrowser
import json
from django.conf import settings
from pathlib import Path

from .cookie_storage import save_cookie, check_cookie_expired, get_cookie

class BilibiliLogin:
    """B站登录工具类，提供扫码登录功能"""
    
    # API 端点
    QR_GENERATE_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    QR_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
    
    headers = {
        "Host": "passport.bilibili.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 状态码
    STATUS_SUCCESS = 0
    STATUS_NOT_SCANNED = 86101
    STATUS_SCANNED_NOT_CONFIRMED = 86090
    STATUS_QR_EXPIRED = 86038
    
    @staticmethod
    def check_cookie_expired():
        """检查B站cookie是否过期"""
        return check_cookie_expired()
    
    @staticmethod
    def generate_qrcode():
        """申请B站登录二维码"""
        try:
            response = requests.get(BilibiliLogin.QR_GENERATE_URL, headers=BilibiliLogin.headers)
            response.raise_for_status()
            
            data = response.json()
            if data['code'] != 0:
                return None, None, f"获取二维码失败: {data['message']}"
            
            qrcode_url = data['data']['url']
            qrcode_key = data['data']['qrcode_key']
            
            return qrcode_key, qrcode_url, None
        except Exception as e:
            return None, None, f"获取二维码异常: {str(e)}"
    
    @staticmethod
    def poll_qrcode_status(qrcode_key):
        """查询二维码扫描状态"""
        try:
            params = {'qrcode_key': qrcode_key}
            response = requests.get(BilibiliLogin.QR_POLL_URL, params=params, headers=BilibiliLogin.headers)
            response.raise_for_status()
            
            data = response.json()
            if data['code'] != 0:
                return None, None, f"查询扫码状态失败: {data['message']}"
            
            # 获取扫码状态
            scan_data = data['data']
            scan_code = scan_data['code']
            scan_message = scan_data['message']
            
            # 如果登录成功，提取cookie
            cookies = {}
            if scan_code == BilibiliLogin.STATUS_SUCCESS:
                # 从响应头中提取cookie
                for cookie in response.cookies:
                    cookies[cookie.name] = cookie.value
                
                # 提取额外信息
                if 'DedeUserID' in cookies and 'SESSDATA' in cookies and 'bili_jct' in cookies:
                    cookies['Expires'] = str(int(time.time()) + 15552000)  # 默认180天过期
                    cookies['gourl'] = 'https%3A%2F%2Fwww.bilibili.com'
                    cookies['first_domain'] = '.bilibili.com'
            
            return scan_code, cookies, scan_message
        except Exception as e:
            return None, None, f"查询扫码状态异常: {str(e)}"
    
    @staticmethod
    def save_cookies(cookies):
        """保存cookie到文件"""
        return save_cookie(cookies)
    
    @staticmethod
    def get_cookies():
        """获取cookie"""
        return get_cookie()
    
    @staticmethod
    def show_qrcode_in_browser(bili_qrcode_url):
        """生成一个包含二维码的HTML文件并在浏览器中显示"""
        # 生成二维码图片数据
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(bili_qrcode_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # 将图片转换为Base64编码字符串
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # 创建美观的HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>哔哩哔哩扫码登录</title>
            <style>
                body {{
                    font-family: "Microsoft YaHei", sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    background-color: #f4f5f7;
                    color: #212121;
                }}
                .container {{
                    background-color: #fff;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                    text-align: center;
                    max-width: 400px;
                    width: 90%;
                }}
                .logo {{
                    width: 120px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #00a1d6;
                    margin-bottom: 20px;
                    font-size: 24px;
                    font-weight: 600;
                }}
                p {{
                    color: #666;
                    font-size: 16px;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }}
                .qrcode-container {{
                    background-color: #fff;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    display: inline-block;
                    margin: 20px 0;
                }}
                .qrcode {{
                    width: 200px;
                    height: 200px;
                }}
                .timer {{
                    color: #fb7299;
                    font-size: 14px;
                    margin-top: 10px;
                    font-weight: 500;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #999;
                }}
                .bilibili-color {{
                    color: #fb7299;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>哔哩哔哩<span class="bilibili-color">扫码登录</span></h1>
                <p>请使用<span class="bilibili-color">哔哩哔哩App</span>扫描下方二维码</p>
                <div class="qrcode-container">
                    <img class="qrcode" src="data:image/png;base64,{img_str}" alt="哔哩哔哩登录二维码">
                </div>
                <p class="timer">二维码有效期为3分钟，请尽快完成扫码</p>
                # <div class="footer">
                #     Cards Service © {time.strftime('%Y')}
                # </div>
            </div>
        </body>
        </html>
        """

        # 将HTML内容写入临时文件
        temp_html_path = "bilibili_login_qrcode.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 在默认浏览器中打开文件
        try:
            webbrowser.open(f"file://{os.path.abspath(temp_html_path)}")
            return True
        except Exception as e:
            print(f"无法在浏览器中打开二维码文件: {e}")
            return False 