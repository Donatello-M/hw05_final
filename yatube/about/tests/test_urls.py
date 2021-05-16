from django.test import Client, TestCase


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

    def setUp(self):
        self.guest = Client()

    def test_about_url_exists_at_desired_location(self):
        for path in StaticURLTests.templates.values():
            with self.subTest(adress=path):
                response = self.guest.get(path)
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        for template, address in StaticURLTests.templates.items():
            with self.subTest(adress=address):
                response = self.guest.get(address)
                self.assertTemplateUsed(response, template)
