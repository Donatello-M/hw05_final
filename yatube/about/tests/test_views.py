from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        for path in StaticViewsTests.templates:
            with self.subTest(adress=path):
                response = self.guest_client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        for path, template in StaticViewsTests.templates.items():
            with self.subTest(value=path):
                response = self.guest_client.get(path)
                self.assertTemplateUsed(response, template)
