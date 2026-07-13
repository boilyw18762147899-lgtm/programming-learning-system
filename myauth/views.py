from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render


def login_view(request):
    """测试用登录：用户名 + 选择身份，无需密码"""
    if request.user.is_authenticated:
        # 已登录：按角色跳转
        return redirect_to_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        role = request.POST.get('role', '').strip()

        if not username:
            messages.error(request, '请输入用户名。')
            return render(request, 'auth/login.html')

        if role not in ('teacher', 'student', 'admin'):
            messages.error(request, '请选择登录身份。')
            return render(request, 'auth/login.html')

        user = authenticate(request, username=username)
        if user is None:
            messages.error(request, f'用户 "{username}" 不存在，请先在后天创建。')
            return render(request, 'auth/login.html')

        if role == 'admin':
            # 管理员：设置 superuser 权限
            user.is_admin = True
            user.is_superuser = True
            user.save()
            login(request, user)
            messages.success(request, f'欢迎管理员，{user.username}！')
            return redirect('admin:index')

        # 教师/学生：加入对应组
        group_name = '老师' if role == 'teacher' else '学生'
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        login(request, user)
        messages.success(request, f'欢迎，{user.username}！已作为{group_name}登录。')
        return redirect_to_role(user)

    return render(request, 'auth/login.html')


def redirect_to_role(user):
    """按角色跳转"""
    if user.isTeacher():
        return redirect('teacher_dashboard')
    if user.isStudent():
        return redirect('student_dashboard')
    return redirect('admin:index')


def logout_view(request):
    """登出"""
    logout(request)
    return redirect('login')
