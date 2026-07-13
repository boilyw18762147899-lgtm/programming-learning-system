from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView,
)

from .forms import AssignmentAnswerForm, AssignmentForm, KnowledgePointForm, QuestionForm
from .mixins import StudentRequiredMixin, TeacherRequiredMixin
from .models import (
    Assignment, AssignmentQuestion, KnowledgePoint, Question,
    StudentPoints, SubmittedAnswer, SubmittedAssignment,
)
from myauth.decorators import teacher_required
from myauth.views import redirect_to_role


# ==================== Home Redirect ====================

@login_required
def home_redirect(request):
    return redirect_to_role(request.user)


# ==================== Teacher Dashboard ====================

class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    template_name = 'teacher/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['assignment_count'] = Assignment.objects.filter(teacher=self.request.user).count()
        ctx['question_count'] = Question.objects.count()
        ctx['kp_count'] = KnowledgePoint.objects.count()
        ctx['student_count'] = Group.objects.get(name='学生').user_set.count()
        ctx['recent_submissions'] = (
            SubmittedAssignment.objects
            .filter(assignment__teacher=self.request.user)
            .select_related('student', 'assignment')
            .order_by('-submitted_at')[:10]
        )
        return ctx


# ==================== Teacher: KnowledgePoint CRUD ====================

class TeacherKnowledgePointListView(TeacherRequiredMixin, ListView):
    model = KnowledgePoint
    template_name = 'teacher/knowledgepoint_list.html'
    context_object_name = 'knowledge_points'
    paginate_by = 15

    def get_queryset(self):
        return KnowledgePoint.objects.annotate(
            question_count=Count('questions')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = KnowledgePoint.objects.values_list(
            'category', flat=True
        ).distinct()
        return ctx


class TeacherKnowledgePointCreateView(TeacherRequiredMixin, CreateView):
    model = KnowledgePoint
    form_class = KnowledgePointForm
    template_name = 'teacher/knowledgepoint_form.html'
    success_url = reverse_lazy('teacher_kp_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, '知识点创建成功！')
        return super().form_valid(form)


class TeacherKnowledgePointUpdateView(TeacherRequiredMixin, UpdateView):
    model = KnowledgePoint
    form_class = KnowledgePointForm
    template_name = 'teacher/knowledgepoint_form.html'
    success_url = reverse_lazy('teacher_kp_list')

    def form_valid(self, form):
        messages.success(self.request, '知识点更新成功！')
        return super().form_valid(form)


class TeacherKnowledgePointDeleteView(TeacherRequiredMixin, DeleteView):
    model = KnowledgePoint
    template_name = 'teacher/knowledgepoint_confirm_delete.html'
    success_url = reverse_lazy('teacher_kp_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '知识点已删除。')
        return super().delete(request, *args, **kwargs)


# ==================== Teacher: Question CRUD ====================

class TeacherQuestionListView(TeacherRequiredMixin, ListView):
    model = Question
    template_name = 'teacher/question_list.html'
    context_object_name = 'questions'
    paginate_by = 15

    def get_queryset(self):
        qs = Question.objects.select_related('knowledge_point').order_by('-created_at')
        kp_id = self.request.GET.get('knowledge_point')
        if kp_id:
            qs = qs.filter(knowledge_point_id=kp_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['knowledge_points'] = KnowledgePoint.objects.all()
        ctx['current_kp'] = self.request.GET.get('knowledge_point', '')
        return ctx


class TeacherQuestionCreateView(TeacherRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'teacher/question_form.html'
    success_url = reverse_lazy('teacher_question_list')

    def form_valid(self, form):
        messages.success(self.request, '题目创建成功！')
        return super().form_valid(form)


class TeacherQuestionUpdateView(TeacherRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'teacher/question_form.html'
    success_url = reverse_lazy('teacher_question_list')

    def form_valid(self, form):
        messages.success(self.request, '题目更新成功！')
        return super().form_valid(form)


class TeacherQuestionDeleteView(TeacherRequiredMixin, DeleteView):
    model = Question
    template_name = 'teacher/question_confirm_delete.html'
    success_url = reverse_lazy('teacher_question_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '题目已删除。')
        return super().delete(request, *args, **kwargs)


# ==================== Teacher: Assignment CRUD ====================

class TeacherAssignmentListView(TeacherRequiredMixin, ListView):
    model = Assignment
    template_name = 'teacher/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        return (
            Assignment.objects
            .filter(teacher=self.request.user)
            .annotate(
                question_count=Count('questions'),
                submission_count=Count('submissions'),
            )
            .order_by('-created_at')
        )


class TeacherAssignmentCreateView(TeacherRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'teacher/assignment_form.html'

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        with transaction.atomic():
            assignment = form.save(commit=False)
            assignment.save()
            # 手动创建 through 关系
            questions = form.cleaned_data['questions']
            for i, q in enumerate(questions):
                AssignmentQuestion.objects.create(
                    assignment=assignment,
                    question=q,
                    order=i,
                )
        messages.success(self.request, '作业创建成功！')
        return redirect('teacher_assignment_detail', pk=assignment.pk)


class TeacherAssignmentDetailView(TeacherRequiredMixin, DetailView):
    model = Assignment
    template_name = 'teacher/assignment_detail.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['aq_list'] = (
            AssignmentQuestion.objects
            .filter(assignment=self.object)
            .select_related('question')
            .order_by('order')
        )
        ctx['submission_count'] = self.object.submissions.count()
        return ctx


class TeacherAssignmentUpdateView(TeacherRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'teacher/assignment_form.html'

    def get_queryset(self):
        return Assignment.objects.filter(teacher=self.request.user)

    def form_valid(self, form):
        with transaction.atomic():
            assignment = form.save()
            # 清空旧关联，重建
            AssignmentQuestion.objects.filter(assignment=assignment).delete()
            questions = form.cleaned_data['questions']
            for i, q in enumerate(questions):
                AssignmentQuestion.objects.create(
                    assignment=assignment, question=q, order=i,
                )
        messages.success(self.request, '作业更新成功！')
        return redirect('teacher_assignment_detail', pk=assignment.pk)


@teacher_required
def teacher_assignment_toggle(request, pk):
    """切换作业启用状态"""
    assignment = get_object_or_404(Assignment, pk=pk, teacher=request.user)
    assignment.is_active = not assignment.is_active
    assignment.save()
    status = '启用' if assignment.is_active else '停用'
    messages.success(request, f'作业已{status}。')
    return redirect('teacher_assignment_detail', pk=pk)


# ==================== Teacher: Submissions ====================

class TeacherSubmissionListView(TeacherRequiredMixin, ListView):
    model = SubmittedAssignment
    template_name = 'teacher/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 20

    def get_queryset(self):
        qs = (
            SubmittedAssignment.objects
            .filter(assignment__teacher=self.request.user)
            .select_related('student', 'assignment')
            .order_by('-submitted_at')
        )
        assignment_id = self.kwargs.get('assignment_id')
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        assignment_id = self.kwargs.get('assignment_id')
        if assignment_id:
            ctx['assignment'] = get_object_or_404(
                Assignment, pk=assignment_id, teacher=self.request.user
            )
        return ctx


class TeacherSubmissionDetailView(TeacherRequiredMixin, DetailView):
    model = SubmittedAssignment
    template_name = 'teacher/submission_detail.html'
    context_object_name = 'submission'

    def get_queryset(self):
        return (
            SubmittedAssignment.objects
            .filter(assignment__teacher=self.request.user)
            .prefetch_related('answers__question')
        )


# ==================== Student Dashboard ====================

class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = 'student/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # 积分
        pts, _ = StudentPoints.objects.get_or_create(student=user)
        ctx['points'] = pts.points

        # 提交统计
        submissions = SubmittedAssignment.objects.filter(student=user)
        ctx['completed_count'] = submissions.count()
        ctx['pending_count'] = (
            Assignment.objects.filter(is_active=True)
            .exclude(submissions__student=user)
            .count()
        )
        avg = submissions.aggregate(avg=Avg('total_count'))['avg'] or 0
        if avg > 0:
            ctx['avg_accuracy'] = round(
                submissions.aggregate(
                    a=Avg('correct_count')
                )['a'] / avg * 100, 1
            )
        else:
            ctx['avg_accuracy'] = 0

        ctx['recent_submissions'] = (
            submissions.select_related('assignment')
            .order_by('-submitted_at')[:5]
        )
        return ctx


# ==================== Student: Assignments ====================

class StudentAssignmentListView(StudentRequiredMixin, ListView):
    model = Assignment
    template_name = 'student/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        return Assignment.objects.filter(is_active=True).annotate(
            question_count=Count('questions')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        submissions = SubmittedAssignment.objects.filter(student=user)
        submitted_map = {s.assignment_id: s.pk for s in submissions}
        # 为每个 assignment 附上 submission_id（模板中判断状态用）
        for a in ctx['object_list']:
            a.submission_id = submitted_map.get(a.pk)
        return ctx


class StudentAssignmentDetailView(StudentRequiredMixin, DetailView):
    model = Assignment
    template_name = 'student/assignment_detail.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # 检查是否已提交
        existing = SubmittedAssignment.objects.filter(
            assignment=self.object, student=user,
        ).first()
        ctx['existing_submission'] = existing

        if not existing:
            aq_list = (
                AssignmentQuestion.objects
                .filter(assignment=self.object)
                .select_related('question')
                .order_by('order')
            )
            ctx['questions'] = aq_list
            ctx['answer_form'] = AssignmentAnswerForm(aq_list)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        # 防重复提交
        if SubmittedAssignment.objects.filter(
            assignment=self.object, student=user
        ).exists():
            messages.warning(request, '您已提交过此作业。')
            return redirect(
                'student_submission_detail',
                pk=SubmittedAssignment.objects.get(
                    assignment=self.object, student=user
                ).pk
            )

        aq_list = list(
            AssignmentQuestion.objects
            .filter(assignment=self.object)
            .select_related('question')
            .order_by('order')
        )

        form = AssignmentAnswerForm(aq_list, data=request.POST)
        if not form.is_valid():
            ctx = self.get_context_data()
            ctx['answer_form'] = form
            return self.render_to_response(ctx)

        with transaction.atomic():
            submission = SubmittedAssignment.objects.create(
                assignment=self.object,
                student=user,
                is_late=self.object.is_expired(),
                total_count=len(aq_list),
            )
            correct = 0
            for aq in aq_list:
                selected = form.cleaned_data[f'question_{aq.question.id}']
                is_correct = (selected == aq.question.correct_answer)
                if is_correct:
                    correct += 1
                SubmittedAnswer.objects.create(
                    submission=submission,
                    question=aq.question,
                    selected_answer=selected,
                    is_correct=is_correct,
                )
            submission.correct_count = correct
            submission.score = correct * self.object.points_per_question
            submission.save()

            # 更新积分
            pts, _ = StudentPoints.objects.get_or_create(student=user)
            pts.points += submission.score
            pts.save()

        messages.success(
            request,
            f'作业提交成功！得分：{submission.score}分 '
            f'（{correct}/{len(aq_list)}）'
        )
        return redirect('student_submission_detail', pk=submission.pk)


# ==================== Student: Submission Detail ====================

class StudentSubmissionDetailView(StudentRequiredMixin, DetailView):
    model = SubmittedAssignment
    template_name = 'student/submission_detail.html'
    context_object_name = 'submission'

    def get_queryset(self):
        return (
            SubmittedAssignment.objects
            .filter(student=self.request.user)
            .prefetch_related('answers__question')
        )


# ==================== Student: Rankings ====================

class StudentRankingsView(StudentRequiredMixin, ListView):
    model = StudentPoints
    template_name = 'student/rankings.html'
    context_object_name = 'rankings'
    paginate_by = 20

    def get_queryset(self):
        return (
            StudentPoints.objects
            .select_related('student')
            .filter(points__gt=0)
            .order_by('-points')
        )
