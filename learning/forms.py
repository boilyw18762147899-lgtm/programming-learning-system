from django import forms
from .models import KnowledgePoint, Question, Assignment, AssignmentQuestion


class KnowledgePointForm(forms.ModelForm):
    class Meta:
        model = KnowledgePoint
        fields = ['title', 'category', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'title': '标题',
            'category': '分类',
            'content': '内容',
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'knowledge_point', 'question_text',
            'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'difficulty', 'explanation',
        ]
        widgets = {
            'correct_answer': forms.RadioSelect(choices=[
                ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'),
            ]),
            'difficulty': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'explanation': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'knowledge_point': '所属知识点',
            'question_text': '题目内容',
            'option_a': '选项A',
            'option_b': '选项B',
            'option_c': '选项C',
            'option_d': '选项D',
            'correct_answer': '正确答案',
            'difficulty': '难度(1-5)',
            'explanation': '答案解析',
        }

    def clean_difficulty(self):
        d = self.cleaned_data['difficulty']
        if d < 1 or d > 5:
            raise forms.ValidationError('难度值必须在1到5之间')
        return d


class AssignmentForm(forms.ModelForm):
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.select_related('knowledge_point').all(),
        widget=forms.CheckboxSelectMultiple,
        label='选择题目',
    )

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'points_per_question', 'deadline', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': '作业标题',
            'description': '作业说明',
            'points_per_question': '每题分值',
            'deadline': '截止时间',
            'is_active': '是否启用',
        }

    def clean_questions(self):
        qs = self.cleaned_data.get('questions', [])
        if len(qs) == 0:
            raise forms.ValidationError('请至少选择一道题目')
        return qs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['questions'].queryset = (
            Question.objects.select_related('knowledge_point').all()
        )
        # 给每个选项加知识点标注
        self.fields['questions'].label_from_instance = lambda q: (
            f"[{q.knowledge_point.title}] {q.question_text[:50]}"
        )


class AssignmentAnswerForm(forms.Form):
    """动态生成的答题表单"""
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for aq in questions:
            q = aq.question
            choices = [
                ('A', f"A. {q.option_a}"),
                ('B', f"B. {q.option_b}"),
                ('C', f"C. {q.option_c}"),
                ('D', f"D. {q.option_d}"),
            ]
            self.fields[f'question_{q.id}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=f'{aq.order + 1}. {q.question_text}',
                required=True,
            )
