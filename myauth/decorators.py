from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


def teacher_required(view_func):
    """要求用户属于'老师'组"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        if not request.user.isTeacher():
            messages.error(request, '您没有权限访问该页面。')
            if request.user.isStudent():
                return redirect('student_dashboard')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """要求用户属于'学生'组"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        if not request.user.isStudent():
            messages.error(request, '您没有权限访问该页面。')
            if request.user.isTeacher():
                return redirect('teacher_dashboard')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
