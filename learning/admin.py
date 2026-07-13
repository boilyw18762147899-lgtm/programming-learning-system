from django.contrib import admin
from .models import Course, Lesson, Assignment, Submission, Enrollment, Progress

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'difficulty', 'is_published', 'created_at']
    list_filter = ['difficulty', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    list_editable = ['is_published']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'teacher', 'cover_image')
        }),
        ('课程设置', {
            'fields': ('difficulty', 'is_published')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 教师只能看到自己的课程
        if not request.user.is_superuser and request.user.is_teacher:
            qs = qs.filter(teacher=request.user)
        return qs

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['course', 'order']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('course', 'title', 'content')
        }),
        ('多媒体', {
            'fields': ('video_url',)
        }),
        ('排序设置', {
            'fields': ('order', 'duration')
        }),
    )

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'difficulty', 'max_score', 'deadline', 'created_at']
    list_filter = ['difficulty', 'lesson__course', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'deadline'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('lesson', 'title', 'description')
        }),
        ('题目内容', {
            'fields': ('question', 'starter_code', 'test_cases')
        }),
        ('评分设置', {
            'fields': ('difficulty', 'max_score', 'deadline')
        }),
    )

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'score', 'status', 'submitted_at', 'graded_at']
    list_filter = ['status', 'submitted_at', 'assignment__lesson__course']
    search_fields = ['student__username', 'assignment__title']
    readonly_fields = ['submitted_at', 'graded_at']
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('提交信息', {
            'fields': ('assignment', 'student', 'code', 'submitted_at')
        }),
        ('评分结果', {
            'fields': ('score', 'status', 'feedback', 'test_result', 'graded_at')
        }),
    )
    
    actions = ['auto_grade_submissions']
    
    def auto_grade_submissions(self, request, queryset):
        """批量自动评分"""
        for submission in queryset:
            submission.auto_grade()
        self.message_user(request, f"已自动评分 {queryset.count()} 份作业")
    auto_grade_submissions.short_description = "自动评分选中的作业"

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'completed', 'get_progress']
    list_filter = ['completed', 'enrolled_at', 'course']
    search_fields = ['student__username', 'course__title']
    date_hierarchy = 'enrolled_at'
    
    def get_progress(self, obj):
        return f"{obj.get_progress_percentage()}%"
    get_progress.short_description = '学习进度'

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'completed', 'time_spent', 'last_accessed']
    list_filter = ['completed', 'lesson__course', 'last_accessed']
    search_fields = ['student__username', 'lesson__title']
    date_hierarchy = 'last_accessed'