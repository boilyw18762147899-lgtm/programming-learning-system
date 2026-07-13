# 开发环境配置文件 —— 不修改原始 settings.py
# 使用: python manage.py runserver --settings=learning_system.settings_dev

from .settings import *

# 覆盖数据库配置为 SQLite（本地开发无需 MySQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
