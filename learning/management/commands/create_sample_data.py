from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from learning.models import Course, Lesson, Assignment, Enrollment, Progress, Submission

User = get_user_model()

class Command(BaseCommand):
    help = '创建示例数据用于测试'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始创建示例数据...\n')

        # 1. 创建用户组
        self.stdout.write('创建用户组...')
        teacher_group, _ = Group.objects.get_or_create(name='老师')
        student_group, _ = Group.objects.get_or_create(name='学生')
        self.stdout.write(self.style.SUCCESS('  ✓ 用户组已就绪'))

        # 2. 创建用户
        self.stdout.write('\n创建用户...')
        
        # 创建教师
        teacher, created = User.objects.get_or_create(
            username='张老师',
            defaults={
                'email': 'zhang@example.com',
                'id_num': 'T20240001'
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            teacher.groups.add(teacher_group)
            self.stdout.write(self.style.SUCCESS(f'  ✓ 创建教师: {teacher.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'  - 教师已存在: {teacher.username}'))

        # 创建学生
        students = []
        for i in range(1, 4):
            student, created = User.objects.get_or_create(
                username=f'学生{i}',
                defaults={
                    'email': f'student{i}@example.com',
                    'id_num': f'S202400{i}'
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                student.groups.add(student_group)
                self.stdout.write(self.style.SUCCESS(f'  ✓ 创建学生: {student.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - 学生已存在: {student.username}'))
            students.append(student)

        # 3. 创建课程
        self.stdout.write('\n创建课程...')
        
        course1, created = Course.objects.get_or_create(
            title='Python 入门',
            defaults={
                'teacher': teacher,
                'description': '从零开始学习 Python 编程语言，掌握基础语法和编程思维。',
                'difficulty': 'beginner',
                'is_published': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 创建课程: {course1.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'  - 课程已存在: {course1.title}'))

        course2, created = Course.objects.get_or_create(
            title='数据结构与算法',
            defaults={
                'teacher': teacher,
                'description': '深入学习常用数据结构和算法，提升编程能力。',
                'difficulty': 'intermediate',
                'is_published': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 创建课程: {course2.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'  - 课程已存在: {course2.title}'))

        # 4. 创建章节
        self.stdout.write('\n创建章节...')
        
        lessons_data = [
            {
                'course': course1,
                'title': '第1课：Python 简介与环境配置',
                'content': '本节课介绍 Python 的特点和应用领域，学习如何安装和配置 Python 开发环境。',
                'order': 1,
                'duration': 30
            },
            {
                'course': course1,
                'title': '第2课：变量与数据类型',
                'content': '学习 Python 的基本数据类型：整数、浮点数、字符串、布尔值等。',
                'order': 2,
                'duration': 45
            },
            {
                'course': course1,
                'title': '第3课：条件语句与循环',
                'content': '掌握 if-else 条件判断和 for、while 循环的使用方法。',
                'order': 3,
                'duration': 60
            },
            {
                'course': course2,
                'title': '第1课：算法复杂度分析',
                'content': '学习时间复杂度和空间复杂度的概念，掌握大O表示法。',
                'order': 1,
                'duration': 50
            },
            {
                'course': course2,
                'title': '第2课：数组与链表',
                'content': '深入理解数组和链表的特点、优缺点及应用场景。',
                'order': 2,
                'duration': 55
            },
        ]

        lessons = []
        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                course=lesson_data['course'],
                title=lesson_data['title'],
                defaults={
                    'content': lesson_data['content'],
                    'order': lesson_data['order'],
                    'duration': lesson_data['duration']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ 创建章节: {lesson.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - 章节已存在: {lesson.title}'))
            lessons.append(lesson)

        # 5. 创建作业
        self.stdout.write('\n创建作业...')
        
        assignments_data = [
            {
                'lesson': lessons[0],
                'title': '编写第一个 Python 程序',
                'description': '编写一个程序，输出 "Hello, Python!"',
                'question': '请编写一个 Python 程序，在控制台输出 "Hello, Python!"',
                'starter_code': '# 在这里编写你的代码\n',
                'test_cases': 'print("Hello, Python!")',
                'difficulty': 'easy',
                'max_score': 10,
                'deadline': timezone.now() + timedelta(days=7)
            },
            {
                'lesson': lessons[1],
                'title': '变量交换',
                'description': '不使用第三个变量交换两个变量的值',
                'question': '给定两个变量 a=5, b=10，在不使用第三个临时变量的情况下交换它们的值',
                'starter_code': 'a = 5\nb = 10\n# 在这里编写你的代码\nprint(a, b)',
                'test_cases': 'a, b = b, a',
                'difficulty': 'easy',
                'max_score': 15,
                'deadline': timezone.now() + timedelta(days=7)
            },
            {
                'lesson': lessons[2],
                'title': '判断奇偶数',
                'description': '编写函数判断一个数是奇数还是偶数',
                'question': '编写一个函数 is_even(n)，如果 n 是偶数返回 True，否则返回 False',
                'starter_code': 'def is_even(n):\n    # 在这里编写你的代码\n    pass\n\nprint(is_even(4))\nprint(is_even(7))',
                'test_cases': 'def is_even(n):\n    return n % 2 == 0',
                'difficulty': 'medium',
                'max_score': 20,
                'deadline': timezone.now() + timedelta(days=7)
            },
        ]

        assignments = []
        for assignment_data in assignments_data:
            assignment, created = Assignment.objects.get_or_create(
                lesson=assignment_data['lesson'],
                title=assignment_data['title'],
                defaults={
                    'description': assignment_data['description'],
                    'question': assignment_data['question'],
                    'starter_code': assignment_data['starter_code'],
                    'test_cases': assignment_data['test_cases'],
                    'difficulty': assignment_data['difficulty'],
                    'max_score': assignment_data['max_score'],
                    'deadline': assignment_data['deadline']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ 创建作业: {assignment.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - 作业已存在: {assignment.title}'))
            assignments.append(assignment)

        # 6. 创建选课记录
        self.stdout.write('\n创建选课记录...')
        
        for student in students:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course1
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {student.username} 选修了 {course1.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - {student.username} 已选修 {course1.title}'))

        # 第一个学生额外选修第二门课
        enrollment, created = Enrollment.objects.get_or_create(
            student=students[0],
            course=course2
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ {students[0].username} 选修了 {course2.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'  - {students[0].username} 已选修 {course2.title}'))

        # 7. 创建学习进度
        self.stdout.write('\n创建学习进度...')
        
        # 第一个学生完成了前两节课
        for lesson in lessons[:2]:
            progress, created = Progress.objects.get_or_create(
                student=students[0],
                lesson=lesson,
                defaults={
                    'completed': True,
                    'time_spent': lesson.duration
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {students[0].username} 完成了 {lesson.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - 进度已存在'))

        # 8. 创建作业提交
        self.stdout.write('\n创建作业提交...')
        
        submission, created = Submission.objects.get_or_create(
            assignment=assignments[0],
            student=students[0],
            defaults={
                'code': 'print("Hello, Python!")',
                'status': 'graded',
                'score': 10,
                'feedback': '完成得很好！',
                'graded_at': timezone.now()
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 创建作业提交记录'))
        else:
            self.stdout.write(self.style.WARNING(f'  - 作业提交已存在'))

        self.stdout.write(self.style.SUCCESS('\n✅ 示例数据创建完成！\n'))
        self.stdout.write('可以使用以下账号登录：')
        self.stdout.write('  教师账号: zhang@example.com / teacher123')
        self.stdout.write('  学生账号: student1@example.com / student123')
        self.stdout.write('  学生账号: student2@example.com / student123')
        self.stdout.write('  学生账号: student3@example.com / student123')