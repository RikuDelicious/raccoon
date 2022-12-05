from urllib.parse import urlparse

from articleapp.models import Post, User
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy
from django.utils import timezone


class DeactivateViewTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(username="testuser_0", password="testuser_0"),
            User.objects.create_user(username="testuser_1", password="testuser_1"),
        ]
        self.url = reverse_lazy("deactivate")
        self.today_datetime = timezone.now()

        posts = [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                slug=f"post_{i}_slug",
                user=self.users[0],
                is_published=True,
                date_publish=self.today_datetime.date(),
            )
            for i in range(0, 5)
        ]
        posts += [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                slug=f"post_{i}_slug",
                user=self.users[0],
                is_published=False,
                date_publish=self.today_datetime.date(),
            )
            for i in range(5, 10)
        ]

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
    
    def test_退会する(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        self.assertTrue("_auth_user_id" in c.session)
        response = c.post(self.url)
        
        # ログアウトしていることの確認
        self.assertFalse("_auth_user_id" in c.session)

        # トップページにリダイレクトされることの確認
        self.assertEqual(response.status_code, 302)
        redirect_url = urlparse(response.headers["Location"])
        self.assertEqual(redirect_url.path, reverse("index"))

        # 再度ログインできないことの確認
        response = c.post(reverse("login"), {"username": "testuser_0", "password": "testuser_0"})
        self.assertFalse("_auth_user_id" in c.session)
        c.login(username="testuser_0", password="testuser_0")
        self.assertFalse("_auth_user_id" in c.session)

        # ユーザーの投稿が全て削除されていることの確認
        self.assertFalse(self.users[0].post_set.exists())

        # ユーザー関連ページにアクセスできないことの確認
        response = c.get(reverse("user_home", kwargs={"username": "testuser_0"}))
        self.assertEqual(response.status_code, 404)

        response = c.get(reverse("user_home_drafts", kwargs={"username": "testuser_0"}))
        self.assertEqual(response.status_code, 404)

        response = c.get(reverse("post_detail", kwargs={"username": "testuser_0", "slug": "post_0_slug"}))
        self.assertEqual(response.status_code, 404)