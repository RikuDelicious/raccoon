from django.test import Client, TestCase
from articleapp.models import User
from django.urls import reverse_lazy, reverse, resolve
from django.contrib.auth import authenticate
from urllib.parse import urlparse


class PasswordChangeViewTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(username="testuser_0", password="testuser_0"),
        ]
        self.url = reverse_lazy("password_change")

    def test_ページアクセス(self):
        c = Client()

        # 未ログインでアクセスするとログインページへリダイレクト
        response = c.get(self.url)
        self.assertEqual(response.status_code, 302)
        redirect_url = urlparse(response.headers["Location"])
        self.assertEqual(redirect_url.path, reverse("login"))

        # ログイン
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_パスワード変更に成功すると設定ページへ遷移(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        response = c.post(
            self.url,
            {
                "old_password": "testuser_0",
                "new_password1": "qpwoeiru",
                "new_password2": "qpwoeiru",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "user_settings_account")

        # パスワードが変わったか確認
        user = authenticate(username="testuser_0", password="qpwoeiru")
        self.assertEqual(user, self.users[0])

    def test_バリデーションエラーでパスワード変更ページに戻る(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        response = c.post(
            self.url,
            {
                "old_password": "testuser_0",
                "new_password1": "eiru",
                "new_password2": "qpwo",
            },
            follow=True,
        )
        self.assertEqual(response.resolver_match.url_name, "password_change")
        self.assertNotEqual(response.context["form"].errors.as_data(), {})

        # パスワードが変わっていないことを確認
        user = authenticate(username="testuser_0", password="eiru")
        self.assertIsNone(user)

        user = authenticate(username="testuser_0", password="qpwo")
        self.assertIsNone(user)
