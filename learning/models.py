from django.db import models
from django.conf import settings
from django.utils import timezone

class KnowledgePoint(models.Model):
    """知识点"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    category = models.CharField(max_length=100, verbose_name='分类', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='knowledge_points',
        verbose_name='创建者'
    )
    
    class Meta:
        db_table = 'learning_knowledge_points'
        verbose_name = '知识点'
        verbose_name_plural = '知识点'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Question(models.Model):
    """题目"""
    ANSWER_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    
    knowledge_point = models.ForeignKey(
        KnowledgePoint,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='知识点'
    )
    question_text = models.TextField(verbose_name='题目内容')
    option_a = models.CharField(max_length=500, verbose_name='选项A')
    option_b = models.CharField(max_length=500, verbose_name='选项B')
    option_c = models.CharField(max_length=500, verbose_name='选项C')
    option_d = models.CharField(max_length=500, verbose_name='选项D')
    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        verbose_name='正确答案'
    )
    difficulty = models.IntegerField(default=3, verbose_name='难度(1-5)')
    explanation = models.TextField(blank=True, verbose_name='答案解析')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'learning_questions'
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.question_text[:30]

class Assignment(models.Model):
    """作业"""
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='说明')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='教师'
    )
    questions = models.ManyToManyField(
        Question,
        through='AssignmentQuestion',
        verbose_name='题目'
    )
    points_per_question = models.IntegerField(default=10, verbose_name='每题分值')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        db_table = 'learning_assignments'
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_expired(self):
        """是否已过期"""
        if not self.deadline:
            return False
        return timezone.now() > self.deadline

class AssignmentQuestion(models.Model):
    """作业-题目关联表"""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        verbose_name='作业'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='题目'
    )
    order = models.IntegerField(default=0, verbose_name='顺序')
    
    class Meta:
        db_table = 'learning_assignment_questions'
        ordering = ['order']
        unique_together = ('assignment', 'question')
        verbose_name = '作业题目'
        verbose_name_plural = '作业题目'

class SubmittedAssignment(models.Model):
    """已提交的作业"""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='作业'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='学生'
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    score = models.IntegerField(default=0, verbose_name='得分')
    correct_count = models.IntegerField(default=0, verbose_name='正确题数')
    total_count = models.IntegerField(default=0, verbose_name='总题数')
    is_late = models.BooleanField(default=False, verbose_name='是否迟交')
    
    class Meta:
        db_table = 'learning_submitted_assignments'
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']
        verbose_name = '提交的作业'
        verbose_name_plural = '提交的作业'
    
    def accuracy_rate(self):
        """正确率"""
        if self.total_count == 0:
            return 0
        return round(self.correct_count / self.total_count * 100, 2)

class SubmittedAnswer(models.Model):
    """提交的答案"""
    submission = models.ForeignKey(
        SubmittedAssignment,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='提交记录'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='题目'
    )
    selected_answer = models.CharField(max_length=1, verbose_name='选择的答案')
    is_correct = models.BooleanField(default=False, verbose_name='是否正确')
    
    class Meta:
        db_table = 'learning_submitted_answers'
        verbose_name = '提交的答案'
        verbose_name_plural = '提交的答案'

class StudentPoints(models.Model):
    """学生积分"""
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='points_record',
        verbose_name='学生'
    )
    points = models.IntegerField(default=0, verbose_name='总积分')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'learning_student_points'
        ordering = ['-points']
        verbose_name = '学生积分'
        verbose_name_plural = '学生积分'
    
    def __str__(self):
        return f'{self.student.username} - {self.points}分'