from articleapp.forms import AccountUpdateForm, ProfileUpdateForm
from articleapp.models import User
from django.test import Client, TestCase
from django.urls import reverse_lazy


class UserSettingsTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(username="testuser_0", password="testuser_0"),
            User.objects.create_user(username="testuser_1", password="testuser_1"),
        ]

        self.url_user_settings = reverse_lazy("user_settings")
        self.url_user_settings_profile = reverse_lazy("user_settings_profile")
        self.url_user_settings_account = reverse_lazy("user_settings_account")

    def test_デフォルトurlで設定ページにアクセスするとリダイレクト(self):
        c = Client()

        # 未ログインはログインページにリダイレクト
        response = c.get(self.url_user_settings, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "login")

        # ログイン済み
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url_user_settings)
        # プロフィール更新ページにリダイレクト
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], self.url_user_settings_profile)

    def test_プロフィール更新ページにアクセス(self):
        c = Client()

        # 未ログインはログインページにリダイレクト
        response = c.get(self.url_user_settings_profile, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "login")

        # ログイン済み
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url_user_settings_profile)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_menu_item"], "profile")
        self.assertListEqual(
            response.context["menu_items"],
            [
                {
                    "name": "profile",
                    "label": "プロフィール",
                    "url_name": "user_settings_profile",
                },
                {
                    "name": "account",
                    "label": "アカウント情報",
                    "url_name": "user_settings_account",
                },
            ],
        )
        self.assertIsInstance(response.context["form"], ProfileUpdateForm)
        self.assertEqual(response.context["form"].is_bound, False)

    def test_アカウント情報ページにアクセス(self):
        c = Client()

        # 未ログインはログインページにリダイレクト
        response = c.get(self.url_user_settings_account, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "login")

        # ログイン済み
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url_user_settings_account)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_menu_item"], "account")
        self.assertListEqual(
            response.context["menu_items"],
            [
                {
                    "name": "profile",
                    "label": "プロフィール",
                    "url_name": "user_settings_profile",
                },
                {
                    "name": "account",
                    "label": "アカウント情報",
                    "url_name": "user_settings_account",
                },
            ],
        )
        self.assertIsInstance(response.context["form"], AccountUpdateForm)
        self.assertEqual(response.context["form"].is_bound, False)

    def test_プロフィール更新(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url_user_settings_profile)
        form = response.context["form"]
