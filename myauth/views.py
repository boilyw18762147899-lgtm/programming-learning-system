from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from myauth.forms import LoginForm, RegisterForm

def user_login(request):
    """登录视图"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # 处理"记住我"
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # 关闭浏览器后过期
            
            messages.success(request, f'欢迎回来，{user.username}！')
            
            # 重定向到原页面或首页
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'myauth/login.html', {'form': form})

def user_register(request):
    """注册视图"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '注册成功！请登录')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'myauth/register.html', {'form': form})

def user_logout(request):
    """登出视图"""
    logout(request)
    messages.info(request, '您已成功退出')
    return redirect('login')

@login_required
def dashboard(request):
    """用户首页（需要登录）"""
    return render(request, 'myauth/dashboard.html')

# ========== 测试视图（保留） ==========

@csrf_exempt
def test_login(request):
    """测试登录页面"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return HttpResponse(f"""
                <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h1 style="color: green;">✓ 登录成功</h1>
                    <p>用户: {user.username}</p>
                    <p>学号/工号: {user.id_num}</p>
                    <p>邮箱: {user.email}</p>
                    <p>is_staff: {user.is_staff}</p>
                    <p>is_superuser: {user.is_superuser}</p>
                    <p>is_active: {user.is_active}</p>
                    <hr>
                    <p><a href="/admin/">前往 Admin 后台</a></p>
                    <p><a href="/test-login/">重新登录</a></p>
                    <p><a href="/dashboard/">前往用户首页</a></p>
                </body>
                </html>
            """)
        else:
            return HttpResponse("""
                <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h1 style="color: red;">✗ 登录失败</h1>
                    <p>学号/邮箱或密码错误</p>
                    <p><a href="/test-login/">返回</a></p>
                </body>
                </html>
            """)
    
    return HttpResponse("""
        <html>
        <head><meta charset="utf-8"></head>
        <body>
            <h2>测试登录</h2>
            <form method="post">
                <p>
                    <label>学号/工号/邮箱：</label><br>
                    <input type="text" name="username" required>
                </p>
                <p>
                    <label>密码：</label><br>
                    <input type="password" name="password" required>
                </p>
                <button type="submit">登录</button>
            </form>
        </body>
        </html>
    """)