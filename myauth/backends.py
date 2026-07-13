from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from myauth.models import MyUser

class CustomAuthBackend(ModelBackend):
    """
    自定义认证后端
    支持：
    1. 学号/工号 + 密码
    2. 邮箱 + 密码
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 尝试通过学号/工号或邮箱查找用户
            user = MyUser.objects.get(
                Q(id_num=username) | Q(email=username)
            )
            
            # 验证密码
            if user.check_password(password):
                return user
            
        except MyUser.DoesNotExist:
            # 防止时序攻击
            MyUser().set_password(password)
            return None
        except MyUser.MultipleObjectsReturned:
            # 如果有多个匹配（理论上不应该发生）
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None