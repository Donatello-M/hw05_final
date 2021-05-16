import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.another_user = User.objects.create_user(username='AnotherUser')
        cls.author = User.objects.create_user(username='Author')
        cls.follow = Follow.objects.create(
            author=cls.author, user=cls.another_user
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Просто описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=cls.image
        )
        cls.author_post = Post.objects.create(
            text='Для подписчиков',
            group=cls.group,
            author=cls.author,
        )
        cls.group_fields = [
            cls.group.title,
            cls.group.slug,
            cls.group.description
        ]
        cls.index_url = reverse('posts:index')
        cls.group_url = reverse(
            'posts:group', kwargs={'slug': 'test-slug'}
        )
        cls.post_view_url = reverse(
            'posts:post_view', kwargs={'username': 'TestUser', 'post_id': 1}
        )
        cls.profile_url = reverse(
            'posts:profile', kwargs={'username': 'TestUser'}
        )
        cls.new_post_url = reverse('posts:new_post')
        cls.post_edit_url = reverse(
            'posts:post_edit', kwargs={'username': 'TestUser', 'post_id': 1}
        )
        cls.follow_url = reverse('posts:follow_index')
        cls.profile_follow_url = reverse(
            'posts:profile_follow', kwargs={'username': 'Author'}
        )
        cls.profile_unfollow_url = reverse(
            'posts:profile_unfollow', kwargs={'username': 'Author'}
        )
        cls.templates_pages_names = {
            cls.index_url: 'posts/index.html',
            cls.group_url: 'group.html',
            cls.new_post_url: 'posts/new_post.html',
            cls.post_edit_url: 'posts/new_post.html',
            cls.post_view_url: 'posts/post.html',
            cls.profile_url: 'posts/profile.html',
            cls.follow_url: 'posts/follow.html'
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.auth_user = Client()
        self.auth_user.force_login(ViewsTests.user)
        self.another_user = Client()
        self.another_user.force_login(ViewsTests.another_user)
        cache.clear()

    def check_post_fields(self, post):
        values = {
            ViewsTests.post.text: post.text,
            ViewsTests.post.group.title: post.group.title,
            ViewsTests.post.author.username: post.author.username,
            ViewsTests.post.image: post.image
        }
        for field, value in values.items():
            with self.subTest(value=value):
                self.assertEqual(value, field)

    def check_form_context(self, response):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.CharField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context['form'][value]
                self.assertIsInstance(field, expected)

    def test_pages_use_correct_template(self):
        for reverse_name, template in ViewsTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_gives_right_context(self):
        response = self.auth_user.get(
            ViewsTests.index_url
        )
        first_object = response.context['page'][1]
        self.check_post_fields(first_object)

    def test_paginator(self):
        posts = [Post(author=ViewsTests.user,
                      text='Тестовый текст',
                      group=ViewsTests.group) for i in range(13)]
        Post.objects.bulk_create(posts)
        response = self.auth_user.get(
            ViewsTests.index_url
        )
        group_resp = self.auth_user.get(
            ViewsTests.group_url
        )
        group_page_cnt = len(group_resp.context['page'])
        page_post_count = len(response.context['page'])
        self.assertEqual(page_post_count, 10)
        self.assertEqual(group_page_cnt, 10)

    def test_group_page_gives_right_context(self):
        response = self.auth_user.get(
            ViewsTests.group_url
        )
        post_first_object = response.context['page'][1]
        self.check_post_fields(post_first_object)
        group_object = response.context['group']
        values = {
            group_object.title: ViewsTests.group_fields[0],
            group_object.slug: ViewsTests.group_fields[1],
            group_object.description: ViewsTests.group_fields[2],
        }
        for expected, value in values.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def text_new_post_page_gives_right_context(self):
        response = self.auth_user.get(
            ViewsTests.new_post_url
        )
        self.check_form_context(response)

    def text_edit_post_page_gives_right_context(self):
        response = self.auth_user.get(
            ViewsTests.post_edit_url
        )
        self.check_form_context(response)

    def test_post_view_page_gives_right_context(self):
        response = self.auth_user.get(
            ViewsTests.post_view_url
        )
        first_object = response.context['post']
        self.check_post_fields(first_object)

    def test_profile_page_gives_right_context(self):
        response = self.auth_user.get(
            ViewsTests.profile_url
        )
        post_object = response.context['page'][0]
        user_object = response.context['user']
        self.assertEqual('TestUser', user_object.username)
        self.check_post_fields(post_object)

    def test_profile_follow(self):
        f_count = Follow.objects.filter(author=ViewsTests.author,
                                        user=ViewsTests.user).count()
        self.auth_user.get(ViewsTests.profile_follow_url)
        s_count = Follow.objects.filter(author=ViewsTests.author,
                                        user=ViewsTests.user).count()
        self.assertEqual(s_count, f_count + 1)

    def test_profile_unfollow(self):
        self.auth_user.get(ViewsTests.profile_follow_url)
        f_count = Follow.objects.filter(author=ViewsTests.author,
                                        user=ViewsTests.user).count()
        self.auth_user.get(ViewsTests.profile_unfollow_url)
        s_count = Follow.objects.filter(author=ViewsTests.author,
                                        user=ViewsTests.user).count()
        self.assertEqual(s_count, f_count - 1)

    def test_follow_post(self):
        response = self.auth_user.get(ViewsTests.follow_url)
        self.assertEqual(len(response.context['page']), 0)
        response = self.another_user.get(ViewsTests.follow_url)
        post = response.context['page'][0]
        self.assertEqual(post, ViewsTests.author_post)

    def test_cache(self):
        self.auth_user.get(ViewsTests.index_url)
        form_data = {
            'text': 'New',
        }
        self.auth_user.post(reverse('posts:post_edit', kwargs={
            'username': 'TestUser', 'post_id': 1
        }), data=form_data, follow=True)
        key = make_template_fragment_key('index_page')
        self.assertIsNotNone(cache.get(key))
