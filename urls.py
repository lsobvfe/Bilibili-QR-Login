from django.urls import path
from . import views

app_name = 'bilibili_login'

urlpatterns = [
    path('status/', views.check_login_status, name='check_login_status'),
    path('qrcode/', views.login_qrcode, name='login_qrcode'),
    path('poll/', views.login_status, name='login_status'),
] 