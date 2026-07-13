from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class Course(models.Model):
    """课程模型"""
    title = models.CharField('课程名称', max_length=200)
    description = models.TextField('课程描述')
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='teaching_courses',
        verbose_name='授课教师',
        limit_choices_to={'is_teacher': True}
    )
    cover_image = models.ImageField(
        '封面图片', 
        upload_to='course_covers/', 
        blank=True, 
        null=True
    )
    difficulty = models.CharField(
        '难度',
        max_length=20,
        choices=[
            ('beginner', '初级'),
            ('intermediate', '中级'),
            ('advanced', '高级'),
        ],
        default='beginner'
    )
    is_published = models.BooleanField('是否发布', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_lesson_count(self):
        """获取章节数量"""
        return self.lessons.count()
    
    def get_student_count(self):
        """获取学生数量"""
        return self.enrollments.count()

class Lesson(models.Model):
    """章节模型"""
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='lessons',
        verbose_name='所属课程'
    )
    title = models.CharField('章节标题', max_length=200)
    content = models.TextField('章节内容')
    video_url = models.URLField('视频链接', blank=True, null=True)
    order = models.PositiveIntegerField('章节顺序', default=0)
    duration = models.PositiveIntegerField('预计学习时长(分钟)', default=30)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '章节'
        verbose_name_plural = '章节'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']  # 同一课程内章节顺序唯一
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_assignment_count(self):
        """获取作业数量"""
        return self.assignments.count()

class Assignment(models.Model):
    """作业模型"""
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='assignments',
        verbose_name='所属章节'
    )
    title = models.CharField('作业标题', max_length=200)
    description = models.TextField('作业描述')
    question = models.TextField('题目要求')
    starter_code = models.TextField('初始代码', blank=True, null=True)
    test_cases = models.JSONField('测试用例', default=list, blank=True)
    max_score = models.PositiveIntegerField(
        '满分',
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    difficulty = models.CharField(
        '难度',
        max_length=20,
        choices=[
            ('easy', '简单'),
            ('medium', '中等'),
            ('hard', '困难'),
        ],
        default='easy'
    )
    deadline = models.DateTimeField('截止时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['lesson', 'created_at']
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"
    
    def is_overdue(self):
        """判断是否过期"""
        if self.deadline:
            return timezone.now() > self.deadline
        return False
    
    def get_submission_count(self):
        """获取提交数量"""
        return self.submissions.count()

class Submission(models.Model):
    """作业提交模型"""
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='submissions',
        verbose_name='作业'
    )
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='submissions',
        verbose_name='学生',
        limit_choices_to={'is_student': True}
    )
    code = models.TextField('提交代码')
    score = models.PositiveIntegerField(
        '得分',
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=[
            ('pending', '待批改'),
            ('passed', '通过'),
            ('failed', '未通过'),
            ('grading', '批改中'),
        ],
        default='pending'
    )
    feedback = models.TextField('教师反馈', blank=True, null=True)
    test_result = models.JSONField('测试结果', default=dict, blank=True)
    submitted_at = models.DateTimeField('提交时间', auto_now_add=True)
    graded_at = models.DateTimeField('批改时间', blank=True, null=True)
    
    class Meta:
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']  # 每个学生每个作业只能提交一次
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    def is_passed(self):
        """判断是否通过"""
        return self.status == 'passed'
    
    def auto_grade(self):
        """自动评分（简化版）"""
        if self.assignment.test_cases:
            passed_tests = 0
            total_tests = len(self.assignment.test_cases)
            
            # 这里应该运行实际的代码测试
            # 目前简化为随机分数
            import random
            passed_tests = random.randint(0, total_tests)
            
            self.score = int((passed_tests / total_tests) * self.assignment.max_score)
            self.status = 'passed' if self.score >= 60 else 'failed'
            self.graded_at = timezone.now()
            self.save()

class Enrollment(models.Model):
    """选课记录模型"""
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='enrollments',
        verbose_name='学生',
        limit_choices_to={'is_student': True}
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='enrollments',
        verbose_name='课程'
    )
    enrolled_at = models.DateTimeField('选课时间', auto_now_add=True)
    completed = models.BooleanField('是否完成', default=False)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)
    
    class Meta:
        verbose_name = '选课记录'
        verbose_name_plural = '选课记录'
        ordering = ['-enrolled_at']
        unique_together = ['student', 'course']  # 每个学生每门课程只能选一次
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    def get_progress_percentage(self):
        """计算学习进度百分比"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        
        completed_lessons = Progress.objects.filter(
            student=self.student,
            lesson__course=self.course,
            completed=True
        ).count()
        
        return int((completed_lessons / total_lessons) * 100)

class Progress(models.Model):
    """学习进度模型"""
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='progress',
        verbose_name='学生',
        limit_choices_to={'is_student': True}
    )
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='progress',
        verbose_name='章节'
    )
    completed = models.BooleanField('是否完成', default=False)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)
    last_accessed = models.DateTimeField('最后访问时间', auto_now=True)
    time_spent = models.PositiveIntegerField('学习时长(分钟)', default=0)
    
    class Meta:
        verbose_name = '学习进度'
        verbose_name_plural = '学习进度'
        ordering = ['-last_accessed']
        unique_together = ['student', 'lesson']
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"
    
    def mark_as_completed(self):
        """标记为已完成"""
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()