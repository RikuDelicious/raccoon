from articleapp import views
from articleapp.forms import UserCreationForm
from articleapp.models import User
from django.contrib.auth import authenticate
from django.test import Client, TestCase
from django.urls import reverse_lazy


class SignUpViewTests(TestCase):
    def setUp(self):
        self.url = reverse_lazy("signup")
        self.users = [
            User.objects.create_user(username="testuser_1", password="testuser_1")
        ]

    def test_未ログインでページアクセス(self):
        c = Client()
        response = c.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], UserCreationForm)
        self.assertEqual(response.context["form"].is_bound, False)

    def test_ログイン済みでページアクセスするとリダイレクト(self):
        c = Client()
        c.login(username="testuser_1", password="testuser_1")
        response = c.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func, views.index)

    def test_正常な入力値でPOSTするとユーザー登録されて自動ログイン(self):
        c = Client()
        response = c.post(
            self.url,
            data={
                "username": "testuser_2",
                "password1": "qpwoeiru",
                "password2": "qpwoeiru",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # 登録されたユーザーのidとパスワードに間違いがないことの確認
        user_authenticated = authenticate(username="testuser_2", password="qpwoeiru")
        self.assertIsNotNone(user_authenticated)

        # 登録したユーザーに自動ログインしていることの確認
        self.assertEqual(int(c.session["_auth_user_id"]), user_authenticated.id)

    def test_バリデーションエラーで再度登録ページを表示(self):
        c = Client()
        response = c.post(
            self.url,
            data={
                "username": "あかさたな",  # Unicode文字は使用不可
                "password1": "qpwo",
                "password2": "qpwoeiru",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 400)  # Bad Request
        self.assertEqual(response.resolver_match.func, views.signup)
        self.assertNotEqual(response.context["form"].errors.as_data(), {})
        self.assertFalse(User.objects.filter(username="あかさたな").exists())
