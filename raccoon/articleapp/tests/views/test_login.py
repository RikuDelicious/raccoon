from articleapp import views
from articleapp.models import User
from django.test import Client, TestCase
from django.urls import reverse_lazy


class LoginViewTests(TestCase):
    def setUp(self):
        self.url = reverse_lazy("login")

    def test_未ログインでページアクセス(self):
        c = Client()
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ログイン済みでアクセスするとリダイレクト(self):
        User.objects.create_user(username="testuser_1", password="testuser_1")
        c = Client()
        c.login(username="testuser_1", password="testuser_1")
        response = c.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func, views.index)
