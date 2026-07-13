from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class MyUserManager(BaseUserManager): 
    """自定义用户管理器""" 
    
    def create_user(self, id_num, username, email=None, password=None, **extra_fields):
        """创建普通用户 - 改为学号为主要字段"""
        if not id_num:
            raise ValueError('学号/工号为必填项')
        if not 4 < len(id_num) < 16: 
            raise ValueError('请调整学号/工号长度') 
        
        # email 可选
        if email:
            email = self.normalize_email(email)
        
        user = self.model( 
            id_num=id_num,
            username=username, 
            email=email,
            **extra_fields
        ) 
        user.set_password(password) 
        user.save(using=self._db) 
        return user

    def create_superuser(self, id_num, username, email=None, password=None, **extra_fields):
        """创建超级用户 - 改为学号为主要字段"""
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        user = self.create_user( 
            id_num=id_num,
            username=username,
            email=email,
            password=password,
            **extra_fields
        ) 
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db) 
        return user

class MyUser(AbstractBaseUser, PermissionsMixin): 
    """自定义用户模型""" 
    
    id_num = models.CharField( 
        max_length=20, 
        verbose_name='学号/工号', 
        unique=True
    )
    username = models.CharField( 
        max_length=16, 
        verbose_name='姓名' 
    )
    email = models.EmailField( 
        verbose_name='邮箱', 
        max_length=255, 
        unique=True,
        null=True,
        blank=True
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
    
    USERNAME_FIELD = 'id_num'  # 改为使用学号/工号登录
    REQUIRED_FIELDS = ['username']  # createsuperuser 时需要输入的额外字段
    
    class Meta: 
        db_table = 'myauth_myuser' 
        verbose_name = '用户' 
        verbose_name_plural = '用户' 
    
    def __str__(self): 
        return f"{self.username} ({self.id_num})"
    
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