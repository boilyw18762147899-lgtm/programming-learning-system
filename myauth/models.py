from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class MyUserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, email, username, id_num, password=None):
        if not email:
            raise ValueError('邮箱为必填项')
        if not 4 < len(id_num) < 16:
            raise ValueError('请调整学号/工号长度')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            id_num=id_num
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, id_num, password):
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            id_num=id_num
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser, PermissionsMixin):
    """自定义用户模型"""
    
    email = models.EmailField(
        verbose_name='邮箱',
        max_length=255,
        unique=True,
    )
    id_num = models.CharField(
        max_length=20,
        verbose_name='学号/工号',
        unique=True
    )
    username = models.CharField(
        max_length=16,
        verbose_name='姓名'
    )
    school = models.CharField(
        max_length=50,
        verbose_name='学校',
        null=True,
        blank=True
    )
    school_short = models.CharField(
        max_length=10,
        verbose_name='学校缩写',
        null=True,
        blank=True
    )
    allow_num = models.IntegerField(
        verbose_name='允许创建数',
        null=True,
        blank=True,
        default=0
    )
    create_num = models.IntegerField(
        verbose_name='剩余可创建数',
        null=True,
        blank=True,
        default=0
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    objects = MyUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'id_num']
    
    class Meta:
        db_table = 'myauth_myuser'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username
    
    def isTeacher(self):
        """判断是否是老师"""
        try:
            return self.groups.filter(name='老师').exists()
        except:
            return False
    
    def isStudent(self):
        """判断是否是学生"""
        try:
            return self.groups.filter(name='学生').exists()
        except:
            return False
    
    @property
    def is_staff(self):
        """是否可以访问admin后台"""
        return self.is_admin or self.is_superuser