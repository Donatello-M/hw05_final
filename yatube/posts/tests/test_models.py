from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='Рандомный текст для теста',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Имя группы'
        )

    def test_group_name(self):
        group = PostModelTest.group
        expected_name = group.title
        self.assertEqual(str(group), expected_name)

    def test_length_of_text(self):
        post = PostModelTest.post
        self.assertEqual(str(post), 'Рандомный текст')
