from django.urls import path
from . import views

urlpatterns = [
    # Home redirect
    path('', views.home_redirect, name='home'),

    # Teacher dashboard
    path('teacher/', views.TeacherDashboardView.as_view(), name='teacher_dashboard'),

    # Teacher: KnowledgePoint CRUD
    path('teacher/knowledge-points/',
         views.TeacherKnowledgePointListView.as_view(), name='teacher_kp_list'),
    path('teacher/knowledge-points/create/',
         views.TeacherKnowledgePointCreateView.as_view(), name='teacher_kp_create'),
    path('teacher/knowledge-points/<int:pk>/edit/',
         views.TeacherKnowledgePointUpdateView.as_view(), name='teacher_kp_edit'),
    path('teacher/knowledge-points/<int:pk>/delete/',
         views.TeacherKnowledgePointDeleteView.as_view(), name='teacher_kp_delete'),

    # Teacher: Question CRUD
    path('teacher/questions/',
         views.TeacherQuestionListView.as_view(), name='teacher_question_list'),
    path('teacher/questions/create/',
         views.TeacherQuestionCreateView.as_view(), name='teacher_question_create'),
    path('teacher/questions/<int:pk>/edit/',
         views.TeacherQuestionUpdateView.as_view(), name='teacher_question_edit'),
    path('teacher/questions/<int:pk>/delete/',
         views.TeacherQuestionDeleteView.as_view(), name='teacher_question_delete'),

    # Teacher: Assignment CRUD
    path('teacher/assignments/',
         views.TeacherAssignmentListView.as_view(), name='teacher_assignment_list'),
    path('teacher/assignments/create/',
         views.TeacherAssignmentCreateView.as_view(), name='teacher_assignment_create'),
    path('teacher/assignments/<int:pk>/',
         views.TeacherAssignmentDetailView.as_view(), name='teacher_assignment_detail'),
    path('teacher/assignments/<int:pk>/edit/',
         views.TeacherAssignmentUpdateView.as_view(), name='teacher_assignment_edit'),
    path('teacher/assignments/<int:pk>/toggle/',
         views.teacher_assignment_toggle, name='teacher_assignment_toggle'),

    # Teacher: Submissions
    path('teacher/submissions/',
         views.TeacherSubmissionListView.as_view(), name='teacher_submission_list'),
    path('teacher/assignments/<int:assignment_id>/submissions/',
         views.TeacherSubmissionListView.as_view(), name='teacher_submission_list_by_assignment'),
    path('teacher/submissions/<int:pk>/',
         views.TeacherSubmissionDetailView.as_view(), name='teacher_submission_detail'),

    # Student dashboard
    path('student/', views.StudentDashboardView.as_view(), name='student_dashboard'),

    # Student: Assignments
    path('student/assignments/',
         views.StudentAssignmentListView.as_view(), name='student_assignment_list'),
    path('student/assignments/<int:pk>/',
         views.StudentAssignmentDetailView.as_view(), name='student_assignment_detail'),

    # Student: Submissions
    path('student/submissions/<int:pk>/',
         views.StudentSubmissionDetailView.as_view(), name='student_submission_detail'),

    # Student: Rankings
    path('student/rankings/',
         views.StudentRankingsView.as_view(), name='student_rankings'),
]
