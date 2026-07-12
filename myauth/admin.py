from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import MyUser

@admin.register(MyUser)
class MyUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'id_num', 'school', 'is_active', 'is_admin']
    list_filter = ['is_active', 'is_admin', 'school', 'groups']
    search_fields = ['username', 'email', 'id_num']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('个人信息', {'fields': ('username', 'id_num', 'school', 'school_short')}),
        ('权限', {'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('其他', {'fields': ('allow_num', 'create_num')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'id_num', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ['groups', 'user_permissions']