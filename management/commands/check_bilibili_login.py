from django.core.management.base import BaseCommand
import time
import sys

from bilibili_login.utils import BilibiliLogin

class Command(BaseCommand):
    help = '检查B站登录状态，如果过期则启动登录流程'

    def handle(self, *args, **options):
        self.stdout.write('检查B站登录状态...')
        
        # 检查cookie是否过期
        if BilibiliLogin.check_cookie_expired():
            self.stdout.write(self.style.WARNING('B站登录已过期，启动登录流程...'))
            
            # 申请二维码
            qrcode_key, qrcode_url, error = BilibiliLogin.generate_qrcode()
            
            if error:
                self.stdout.write(self.style.ERROR(f'获取二维码失败: {error}'))
                sys.exit(1)
            
            # 生成二维码并在浏览器中显示
            BilibiliLogin.show_qrcode_in_browser(qrcode_url)
            self.stdout.write('请使用B站App扫描二维码进行登录...')
            
            # 轮询扫码状态
            max_attempts = 60  # 最多尝试60次，每次3秒，共3分钟
            attempt = 0
            
            while attempt < max_attempts:
                # 查询扫码状态
                scan_code, cookies, message = BilibiliLogin.poll_qrcode_status(qrcode_key)
                
                # 根据扫码状态处理
                if scan_code == BilibiliLogin.STATUS_SUCCESS:
                    # 登录成功，保存cookie
                    if cookies and BilibiliLogin.save_cookies(cookies):
                        self.stdout.write(self.style.SUCCESS('登录成功，cookie已保存'))
                        return
                    else:
                        self.stdout.write(self.style.ERROR('登录成功，但cookie保存失败'))
                        sys.exit(1)
                elif scan_code == BilibiliLogin.STATUS_QR_EXPIRED:
                    # 二维码已过期
                    self.stdout.write(self.style.ERROR('二维码已过期，请重新运行命令'))
                    sys.exit(1)
                elif scan_code == BilibiliLogin.STATUS_SCANNED_NOT_CONFIRMED:
                    # 已扫描未确认，继续等待
                    self.stdout.write('二维码已扫描，等待确认...')
                elif scan_code == BilibiliLogin.STATUS_NOT_SCANNED:
                    # 未扫描，继续等待
                    if attempt % 5 == 0:  # 每15秒提示一次
                        self.stdout.write('等待扫描二维码...')
                
                # 等待3秒后再次查询
                time.sleep(3)
                attempt += 1
            
            if attempt >= max_attempts:
                self.stdout.write(self.style.ERROR('二维码扫描超时，请重新运行命令'))
                sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS('B站登录状态有效')) 