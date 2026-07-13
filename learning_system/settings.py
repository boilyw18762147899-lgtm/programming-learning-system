import os
import pymysql
pymysql.install_as_MySQLdb()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'django-insecure-stitp-2024-project-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['*']

# 应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'learning',      # 学习系统app
    'myauth',        # 认证app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'learning_system.urls'  # 或者是 'programming_learning_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'learning_system.wsgi.application'

# ========== 数据库配置 ==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'STITP',
        'USER': 'root',
        'PASSWORD': '666666',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 使用自定义用户模型
AUTH_USER_MODEL = 'myauth.MyUser'
AUTHENTICATION_BACKENDS = ['myauth.backends.EmailBackend']

# 密码验证（开发阶段简化）
AUTH_PASSWORD_VALIDATORS = []

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# 静态文件配置
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 登录配置
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Django 3.2 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 认证后端配置
AUTHENTICATION_BACKENDS = [
    'myauth.backends.CustomAuthBackend',  # 自定义认证后端
    'django.contrib.auth.backends.ModelBackend',  # Django 默认后端（备用）
]

# 登录相关配置
LOGIN_URL = 'login'  # 未登录时重定向到登录页
LOGIN_REDIRECT_URL = 'dashboard'  # 登录成功后重定向到用户首页
LOGOUT_REDIRECT_URL = 'login'  # 登出后重定向到登录页