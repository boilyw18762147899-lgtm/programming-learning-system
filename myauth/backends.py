from django.contrib.auth.backends import ModelBackend
from .models import MyUser


class EmailBackend(ModelBackend):
    """测试用：不验证密码，只按用户名查找"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            return MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            return None
        except MyUser.MultipleObjectsReturned:
            return MyUser.objects.filter(username=username).first()
