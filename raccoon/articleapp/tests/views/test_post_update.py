import string
import random
from urllib.parse import urlparse

from articleapp.forms import PostForm
from articleapp.models import Post, Tag, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

class PostUpdateTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(username=f"testuser_{i}", password=f"testuser_{i}")
            for i in range(2)
        ]
    
    def test_ページアクセス(self):
        c = Client()
        post = Post.objects.create(
                title=f"post_0",
                body=f"post_0_body",
                user=self.users[0],
                is_published=True,
                date_publish=(timezone.now().date()),
            )
        url = reverse("post_update", kwargs={"username": post.user.username, "slug": post.slug})
        # 未ログインでアクセスするとログインページにリダイレクト
        response = c.get(url)
        self.assertEqual(response.status_code, 302)
        redirect_url = urlparse(response.headers["Location"])
        self.assertEqual(redirect_url.path, reverse("login"))

        # ログイン済みでアクセスする
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        # 投稿が存在しない場合は404
        url = reverse("post_update", kwargs={"username": post.user.username, "slug": "hogehoge"})
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

        # ログイン済みで他のユーザーの投稿にアクセスすると404
        post = Post.objects.create(
                title=f"post_1",
                body=f"post_1_body",
                user=self.users[1],
                is_published=True,
                date_publish=(timezone.now().date()),
            )
        url = reverse("post_update", kwargs={"username": post.user.username, "slug": post.slug})
        response = c.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_ページアクセス時のコンテクスト(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        tags = [Tag.objects.create(name=f"tag_{i}") for i in range(5)]
        post = Post.objects.create(
                title=f"post_0",
                body=f"post_0_body",
                user=self.users[0],
                is_published=True,
                date_publish=(timezone.now().date()),
            )
        post.tags.add(*tags)
        url = reverse("post_update", kwargs={"username": post.user.username, "slug": post.slug})

        response = c.get(url)
        self.assertEqual(response.context["form_action_url"], url)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(response.context["form"].instance, post)

        # tage_textフィールドに紐づけたタグが復元することを確認する
        self.assertEqual(response.context["form"].initial["tags_text"], "tag_0 tag_1 tag_2 tag_3 tag_4")

    
