from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """要求用户属于'老师'组"""

    def test_func(self):
        return self.request.user.isTeacher()

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.isStudent():
            messages.error(self.request, '您没有权限访问该页面。')
            return redirect('student_dashboard')
        return super().handle_no_permission()


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """要求用户属于'学生'组"""

    def test_func(self):
        return self.request.user.isStudent()

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.isTeacher():
            messages.error(self.request, '您没有权限访问该页面。')
            return redirect('teacher_dashboard')
        return super().handle_no_permission()
