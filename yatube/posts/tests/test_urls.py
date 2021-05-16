from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.not_author = User.objects.create_user(username='Not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Просто описание'
        )
        cls.post = Post.objects.create(
            text='Оооочень интересный текст',
            group=cls.group,
            author=cls.user
        )
        cls.public_urls_templates = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'group.html',
            f'/{cls.user.username}/': 'posts/profile.html',
            f'/{cls.post.author.username}/{cls.post.pk}/': 'posts/post.html',
        }
        cls.private_urls_templates = {
            '/new/':
                'posts/new_post.html',
            f'/{cls.post.author.username}/{cls.post.pk}/edit/':
                'posts/new_post.html'
        }

    def setUp(self):
        self.guest = Client()
        self.auth_user = Client()
        self.auth_user.force_login(StaticURLTests.user)
        self.auth_not_author = Client()
        self.auth_not_author.force_login(StaticURLTests.not_author)

    def test_public_pages(self):
        """Страницы, доступные всем"""
        for path in StaticURLTests.public_urls_templates:
            with self.subTest(adress=path):
                response = self.guest.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_page_for_user(self):
        """Страница нового поста для пользователя"""
        response = self.auth_user.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_page_for_guest(self):
        """Страница нового поста для гостя"""
        for path in StaticURLTests.private_urls_templates:
            with self.subTest(adress=path):
                response = self.guest.get(path)
                red_path = f'/auth/login/?next={path}'
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, red_path)

    def test_not_author_get_edit_page(self):
        """Переводит гостя на страницу регистрации"""
        response = self.auth_not_author.get('/TestUser/1/edit/')
        self.assertRedirects(response, '/TestUser/1/')

    def test_public_templates_for_guest(self):
        for address, template in StaticURLTests.public_urls_templates.items():
            with self.subTest(adress=address):
                response = self.guest.get(address)
                self.assertTemplateUsed(response, template)

    def test_private_templates_for_user(self):
        for address, template in StaticURLTests.private_urls_templates.items():
            with self.subTest(adress=address):
                response = self.auth_user.get(address)
                self.assertTemplateUsed(response, template)

    def test_404_page(self):
        response = self.auth_user.get('/User/15/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')
