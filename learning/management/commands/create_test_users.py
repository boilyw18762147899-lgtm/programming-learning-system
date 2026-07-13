from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = '创建测试用户'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始创建测试用户...\n')

        # 清除旧的测试用户
        old_users = ['admin001', 'T20240001', 'S2024001', 'S2024002', 'S2024003']
        for id_num in old_users:
            try:
                user = User.objects.get(id_num=id_num)
                user.delete()
                self.stdout.write(f'✓ 已删除旧用户: {id_num}')
            except User.DoesNotExist:
                pass

        self.stdout.write('')

        # 确保学生组存在
        student_group, _ = Group.objects.get_or_create(name='学生')

        # 新的测试用户数据
        test_users = [
            {
                'id_num': 'B24041910',
                'username': '王博立',
                'email': 'B24041910@njupt.edu.cn',
                'password': '123456',
            },
            {
                'id_num': 'B24041908',
                'username': '于涵竹',
                'email': 'B24041908@njupt.edu.cn',
                'password': '123456',
            },
            {
                'id_num': 'B24041829',
                'username': '黄军炀',
                'email': 'B24041829@njupt.edu.cn',
                'password': '123456',
            },
        ]

        # 创建新用户
        for user_data in test_users:
            try:
                # 检查用户是否已存在
                user, created = User.objects.get_or_create(
                    id_num=user_data['id_num'],
                    defaults={
                        'username': user_data['username'],
                        'email': user_data['email'],
                    }
                )

                if created:
                    user.set_password(user_data['password'])
                    user.is_active = True
                    user.save()
                    # 添加到学生组
                    user.groups.add(student_group)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ 创建用户: {user_data['username']} ({user_data['id_num']})"
                        )
                    )
                else:
                    # 用户已存在，更新密码
                    user.username = user_data['username']
                    user.email = user_data['email']
                    user.set_password(user_data['password'])
                    user.is_active = True
                    user.save()
                    user.groups.add(student_group)
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ 用户已存在，已更新: {user_data['username']} ({user_data['id_num']})"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ 创建用户失败 {user_data['username']}: {str(e)}")
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ 测试用户创建完成！\n'))
        
        # 显示登录信息
        self.stdout.write('=' * 60)
        self.stdout.write('登录信息：')
        self.stdout.write('=' * 60)
        for user_data in test_users:
            self.stdout.write(f"学号: {user_data['id_num']}")
            self.stdout.write(f"姓名: {user_data['username']}")
            self.stdout.write(f"邮箱: {user_data['email']}")
            self.stdout.write(f"密码: {user_data['password']}")
            self.stdout.write('-' * 60)