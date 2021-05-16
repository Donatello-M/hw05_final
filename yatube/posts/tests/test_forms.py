from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.commentator = User.objects.create_user(username='Commentator')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Просто описание'
        )
        cls.other_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='other-test-slug',
            description='Еще одно просто описание'
        )
        cls.post = Post.objects.create(
            text='old',
            group=cls.other_group,
            author=cls.user
        )

    def setUp(self):
        self.auth_user = Client()
        self.commentator = Client()
        self.auth_user.force_login(FormTests.user)
        self.commentator.force_login(FormTests.commentator)

    def test_valid_for_form(self):
        post_count = Post.objects.count()
        gr_p_cnt = Post.objects.filter(group=FormTests.group.id).count()
        og_p_cnt = Post.objects.filter(
            group=FormTests.other_group.id).count()
        form_data = {
            'text': 'Тестовый текст',
            'group': FormTests.group.id,
        }
        response = self.auth_user.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        reverse_path = reverse('posts:index')
        self.assertRedirects(response, reverse_path)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.filter(group=FormTests.group.id).count(),
                         gr_p_cnt + 1)
        self.assertEqual(
            Post.objects.filter(group=FormTests.other_group.id).count(),
            og_p_cnt)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=FormTests.group.id,
            ).exists()
        )

    def test_edit_changes_post(self):
        old_post = Post.objects.get(pk=1)
        old_text = old_post.text
        form_data = {
            'text': 'New',
            'group': FormTests.other_group.id,
        }
        response = self.auth_user.post(
            reverse('posts:post_edit', kwargs={
                'username': 'TestUser', 'post_id': 1,
            }),
            data=form_data,
            follow=True
        )
        edit_post = Post.objects.get(pk=1)
        edit_text = edit_post.text
        reverse_path = '/TestUser/1/'
        self.assertRedirects(response, reverse_path)
        self.assertNotEqual(old_text, edit_text)

    def test_comments(self):
        form_data = {
            'text': 'Комментарий'
        }
        response = self.commentator.post(
            reverse('posts:add_comment', kwargs={
                'username': 'TestUser', 'post_id': 1,
            }),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.get(author=FormTests.commentator)
        comment_text = comment.text
        reverse_path = '/TestUser/1/'
        self.assertEqual(comment_text, 'Комментарий')
        self.assertRedirects(response, reverse_path)
