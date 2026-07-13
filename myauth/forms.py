from django import forms
from django.contrib.auth import authenticate
from myauth.models import MyUser

class LoginForm(forms.Form):
    """登录表单"""
    username = forms.CharField(
        label='学号/工号/邮箱',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入学号/工号或邮箱',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )
    remember_me = forms.BooleanField(
        label='记住我',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError('学号/邮箱或密码错误')
            if not self.user.is_active:
                raise forms.ValidationError('账号已被禁用')
        
        return cleaned_data
    
    def get_user(self):
        return getattr(self, 'user', None)

class RegisterForm(forms.ModelForm):
    """注册表单"""
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '至少6位'
        }),
        min_length=6
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '再次输入密码'
        })
    )
    
    class Meta:
        model = MyUser
        fields = ['id_num', 'username', 'email']
        labels = {
            'id_num': '学号',
            'username': '姓名',
            'email': '邮箱'
        }
        widgets = {
            'id_num': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：B24041910'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入真实姓名'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：student@njupt.edu.cn'
            })
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次密码输入不一致')
        return password2
    
    def clean_id_num(self):
        id_num = self.cleaned_data.get('id_num')
        if MyUser.objects.filter(id_num=id_num).exists():
            raise forms.ValidationError('该学号已被注册')
        return id_num
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and MyUser.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user