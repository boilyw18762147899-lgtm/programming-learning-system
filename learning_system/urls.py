from django.contrib import admin
from django.urls import path
from myauth import views

urlpatterns = [
    # Admin 后台
    path('admin/', admin.site.urls),
    
    # 用户认证
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 测试页面（保留）
    path('test-login/', views.test_login, name='test_login'),
    
    # 默认首页重定向到登录
    path('', views.user_login, name='home'),
]