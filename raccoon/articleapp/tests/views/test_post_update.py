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
        url = reverse(
            "post_update", kwargs={"username": post.user.username, "slug": post.slug}
        )
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
        url = reverse(
            "post_update", kwargs={"username": post.user.username, "slug": "hogehoge"}
        )
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
        url = reverse(
            "post_update", kwargs={"username": post.user.username, "slug": post.slug}
        )
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
        url = reverse(
            "post_update", kwargs={"username": post.user.username, "slug": post.slug}
        )

        response = c.get(url)
        self.assertEqual(response.context["form_action_url"], url)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(response.context["form"].instance, post)

    def test_フォーム独自フィールドの初期値(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        tags = [Tag.objects.create(name=f"tag_{i}") for i in range(5)]
        posts = [
            Post.objects.create(
                title=f"post_0",
                body=f"post_0_body",
                user=self.users[0],
                is_published=True,
                date_publish=(timezone.now().date()),
            ),
            Post.objects.create(
                title=f"post_0",
                body=f"post_0_body",
                user=self.users[0],
                is_published=False,
                date_publish=(timezone.now().date()),
            ),
        ]
        posts[0].tags.add(*tags)

        # posts[0]でテスト
        url = reverse(
            "post_update",
            kwargs={"username": posts[0].user.username, "slug": posts[0].slug},
        )
        response = c.get(url)
        # tage_textフィールドに紐づけたタグが復元することを確認する
        self.assertEqual(
            response.context["form"].initial["tags_text"],
            "tag_0 tag_1 tag_2 tag_3 tag_4",
        )
        # save_optionの確認
        self.assertEqual(
            response.context["form"].initial["save_option"],
            "save_and_publish",
        )

        # posts[1]でテスト
        url = reverse(
            "post_update",
            kwargs={"username": posts[1].user.username, "slug": posts[1].slug},
        )
        response = c.get(url)
        # tage_textフィールドが空であることを確認
        self.assertEqual(
            response.context["form"].initial["tags_text"],
            "",
        )
        # save_optionの確認
        self.assertEqual(
            response.context["form"].initial["save_option"],
            "save_as_draft",
        )

    def test_値を変更せずに保存(self):
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

        # フォーム取得
        url = reverse(
            "post_update",
            kwargs={"username": post.user.username, "slug": post.slug},
        )
        response = c.get(url)
        form_initial = response.context["form"].initial
        post_data = {
            "title": form_initial["title"],
            "slug": form_initial["slug"],
            "body": form_initial["body"],
            "tags_text": form_initial["tags_text"],
            "save_option": form_initial["save_option"],
        }
        # フォーム送信して投稿一覧に遷移
        response = c.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        redirect_url = urlparse(response.headers["Location"])
        self.assertEqual(
            redirect_url.path,
            reverse("user_home", kwargs={"username": "testuser_0"}),
        )
        # 投稿に変更がないことを確認
        post_new = Post.objects.get(user=post.user, slug=post.slug)
        self.assertEqual(post.title, post_new.title)
        self.assertEqual(post.slug, post_new.slug)
        self.assertQuerysetEqual(
            post.tags.order_by("name").all(), post_new.tags.order_by("name").all()
        )
        self.assertEqual(post.body, post_new.body)
        self.assertEqual(post.user, post_new.user)
        self.assertEqual(post.is_published, post_new.is_published)
        self.assertEqual(post.date_publish, post_new.date_publish)

    def test_フォーム_titleフィールド(self):
        pass
