from django.contrib import admin
from .models import (
    KnowledgePoint, Question, Assignment, AssignmentQuestion,
    SubmittedAssignment, SubmittedAnswer, StudentPoints
)

@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_by', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'knowledge_point', 'correct_answer', 'difficulty', 'created_at']
    list_filter = ['difficulty', 'knowledge_point', 'created_at']
    search_fields = ['question_text']
    
    def question_text_short(self, obj):
        return obj.question_text[:50]
    question_text_short.short_description = '题目'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'points_per_question', 'deadline', 'is_active', 'created_at']
    list_filter = ['is_active', 'teacher', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    filter_horizontal = ['questions']

@admin.register(SubmittedAssignment)
class SubmittedAssignmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'score', 'correct_count', 'total_count', 'accuracy', 'submitted_at']
    list_filter = ['is_late', 'submitted_at']
    search_fields = ['student__username', 'assignment__title']
    
    def accuracy(self, obj):
        return f"{obj.accuracy_rate()}%"
    accuracy.short_description = '正确率'

@admin.register(StudentPoints)
class StudentPointsAdmin(admin.ModelAdmin):
    list_display = ['student', 'points', 'updated_at']
    search_fields = ['student__username']
    ordering = ['-points']