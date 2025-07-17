# B站登录模块 (bilibili_login)

这是一个通过客户端扫码获取Bilibili Cookie的Django模块，可以在需要B站Cookie的地方使用

![image-20250717203658844](/image-20250717203658844.png)

## 功能特点

- 检查B站登录状态
- 生成B站登录二维码
- 轮询扫码状态
- 保存登录Cookie
- 提供登录状态检查的装饰器
- 提供命令行工具检查登录状态

## 功能具体说明

### 1. 检查登录状态

在需要B站登录的视图函数中使用`@bilibili_login_required`装饰器：

```python
from bilibili_login.decorators import bilibili_login_required

@bilibili_login_required
def your_view(request):
    # 你的视图函数代码
    pass
```

### 2. 命令行检查登录状态

使用以下命令检查B站登录状态，如果过期则自动启动登录流程：

```bash
python manage.py check_bilibili_login
```

### 3. API接口

模块提供了以下API接口：

- 检查登录状态: `GET /bilibili/status/`
- 生成登录二维码: `GET /bilibili/qrcode/`
- 轮询扫码状态: `GET /bilibili/poll/?qrcode_key=xxx`

### 4. 在代码中使用

```python
from bilibili_login.utils import BilibiliLogin
from bilibili_login.cookie_storage import get_cookie

# 检查登录状态
is_expired = BilibiliLogin.check_cookie_expired()

# 获取Cookie
cookie = get_cookie()

# 如果需要手动登录
if is_expired:
    # 申请二维码
    qrcode_key, qrcode_url, error = BilibiliLogin.generate_qrcode()
    
    # 显示二维码
    BilibiliLogin.show_qrcode_in_browser(qrcode_url)
    
    # 轮询扫码状态
    scan_code, cookies, message = BilibiliLogin.poll_qrcode_status(qrcode_key)
    
    # 保存Cookie
    if cookies:
        BilibiliLogin.save_cookies(cookies)
```

### 5. Cookie的储存位置

Cookie存储在`bilibili_login/data/bilibili_cookie.json`文件中，具体字段如下所示：
```json
{
    "SESSDATA": "",
    "bili_jct": "",
    "DedeUserID": "",
    "DedeUserID__ckMd5": "",
    "sid": "",
    "Expires": "0",
    "gourl": "https%3A%2F%2Fwww.bilibili.com",
    "first_domain": ".bilibili.com"
}
```

## 目录结构

```
bilibili_login/
├── __init__.py            # 应用初始化文件
├── apps.py                # 应用配置
├── cookie_storage.py      # Cookie存储模块
├── decorators.py          # 装饰器模块
├── data/                  # 数据存储目录
│   └── bilibili_cookie.json  # Cookie存储文件
├── management/            # 管理命令目录
│   ├── __init__.py
│   └── commands/          # 命令目录
│       ├── __init__.py
│       └── check_bilibili_login.py  # 检查登录状态命令
├── signals.py             # 信号处理器
├── urls.py                # URL配置
├── utils.py               # 工具类
└── views.py               # 视图函数
```

## 安装方法

1. 将`bilibili_login`目录复制到你的Django项目中
2. 在项目的`settings.py`中添加应用：

```python
INSTALLED_APPS = [
    # ...其他应用...
    'bilibili_login',
]
```

3. 在项目的`urls.py`中添加URL配置：

```python
from django.urls import path, include

urlpatterns = [
    # ...其他URL配置...
    path('bilibili/', include('bilibili_login.urls')),
]
```

## 依赖项

Django
```python
pip install Django
```
requests
```python
pip install requests
```
qrcode
```python
pip install qrcode
```
Pillow (PIL)
```python
pip install Pillow
```

## 文件说明

### cookie_storage.py

Cookie存储模块，负责Cookie的加载、保存和过期检查。

主要函数：
- `load_cookie()`: 加载Cookie
- `save_cookie(cookie_dict)`: 保存Cookie
- `check_cookie_expired()`: 检查Cookie是否过期
- `get_cookie()`: 获取Cookie

### utils.py

B站登录工具类，提供扫码登录相关功能。

主要方法：
- `BilibiliLogin.check_cookie_expired()`: 检查Cookie是否过期
- `BilibiliLogin.generate_qrcode()`: 申请B站登录二维码
- `BilibiliLogin.poll_qrcode_status(qrcode_key)`: 查询扫码状态
- `BilibiliLogin.save_cookies(cookies)`: 保存Cookie
- `BilibiliLogin.get_cookies()`: 获取Cookie
- `BilibiliLogin.show_qrcode_in_browser(bili_qrcode_url)`: 显示二维码

### views.py

视图函数，提供Web接口。

主要视图：
- `check_login_status(request)`: 检查登录状态
- `login_qrcode(request)`: 生成登录二维码
- `login_status(request)`: 获取登录状态

### decorators.py

装饰器模块，提供登录状态检查装饰器。

主要装饰器：
- `bilibili_login_required`: 检查B站登录状态的装饰器

### management/commands/check_bilibili_login.py

命令行工具，用于检查登录状态并启动登录流程。

使用方法：
```bash
python manage.py check_bilibili_login
```

### signals.py

信号处理器，用于在应用启动时检查登录状态。

## 注意事项

1. Cookie存储在`bilibili_login/data/bilibili_cookie.json`文件中，确保该目录具有写入权限。
2. 二维码有效期为3分钟，请在生成后尽快扫描。
3. 登录成功后，Cookie默认有效期为180天。



