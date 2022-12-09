from django.test import Client, TestCase
from django.urls import reverse
from urllib.parse import urlparse
from articleapp.models import Post, Tag, User
from articleapp.forms import PostForm
from django.utils import timezone


class PostCreateViewTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(username=f"testuser_{i}", password=f"testuser_{i}")
            for i in range(1)
        ]
        self.url = reverse("post_create")

    def test_ページアクセス(self):
        c = Client()

        # 未ログインでアクセスするとログインページにリダイレクト
        response = c.get(self.url)
        self.assertEqual(response.status_code, 302)
        redirect_url = urlparse(response.headers["Location"])
        self.assertEqual(redirect_url.path, reverse("login"))

        # ログイン済みでアクセスする
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ページアクセス時のコンテクスト(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url)

        self.assertEqual(response.context["form_action_url"], self.url)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertFalse(response.context["form"].is_bound)

    def test_正しい値でフォーム送信して下書き保存(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        # フォーム取得
        response = c.get(self.url)
        form = response.context["form"]

        # フォーム送信
        post_data = {
            "title": "タイトル",
            "tags_text": "Python Django",
            "slug": form.get_initial_for_field(form.fields["slug"], "slug"),
            "body": "投稿本文",
            "save_option": form.get_initial_for_field(
                form.fields["save_option"], "save_option"
            ),
        }
        response = c.post(self.url, post_data)

        # 成功すると下書き一覧ページにリダイレクト
        self.assertEqual(response.status_code, 302)
        redirect_url = urlparse(response.headers["Location"])
        self.assertEqual(
            redirect_url.path,
            reverse("user_home_drafts", kwargs={"username": "testuser_0"}),
        )

        # 投稿が作成されていることの確認
        self.assertTrue(
            Post.objects.filter(user=self.users[0], slug=post_data["slug"]).exists()
        )
        # タグが作成されていることの確認
        self.assertTrue(Tag.objects.filter(name="Python").exists())
        self.assertTrue(Tag.objects.filter(name="Django").exists())
        # 作成した投稿の各属性が正しいことの確認
        post = Post.objects.get(user=self.users[0], slug=post_data["slug"])
        self.assertEqual(post.title, "タイトル")
        self.assertEqual(post.body, "投稿本文")
        self.assertEqual(post.user, self.users[0])
        self.assertEqual(post.slug, post_data["slug"])
        self.assertListEqual(
            list(post.tags.all().order_by("name")),
            list(Tag.objects.filter(name__in=["Python", "Django"]).order_by("name")),
        )
        self.assertFalse(post.is_published)
        self.assertIsNone(post.date_publish)

    def test_正しい値でフォーム送信して投稿公開(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        # フォーム取得
        response = c.get(self.url)
        form = response.context["form"]

        # フォーム送信
        post_data = {
            "title": "タイトル",
            "tags_text": "Python Django",
            "slug": form.get_initial_for_field(form.fields["slug"], "slug"),
            "body": "投稿本文",
            "save_option": "save_and_publish",
        }
        response = c.post(self.url, post_data)

        # 成功すると投稿一覧ページにリダイレクト
        self.assertEqual(response.status_code, 302)
        redirect_url = urlparse(response.headers["Location"])
        self.assertEqual(
            redirect_url.path,
            reverse("user_home", kwargs={"username": "testuser_0"}),
        )

        # 投稿が作成されていることの確認
        self.assertTrue(
            Post.objects.filter(user=self.users[0], slug=post_data["slug"]).exists()
        )
        # タグが作成されていることの確認
        self.assertTrue(Tag.objects.filter(name="Python").exists())
        self.assertTrue(Tag.objects.filter(name="Django").exists())
        # 作成した投稿の各属性が正しいことの確認
        post = Post.objects.get(user=self.users[0], slug=post_data["slug"])
        self.assertEqual(post.title, "タイトル")
        self.assertEqual(post.body, "投稿本文")
        self.assertEqual(post.user, self.users[0])
        self.assertEqual(post.slug, post_data["slug"])
        self.assertListEqual(
            list(post.tags.all().order_by("name")),
            list(Tag.objects.filter(name__in=["Python", "Django"]).order_by("name")),
        )
        self.assertTrue(post.is_published)
        self.assertEqual(post.date_publish, timezone.localtime().date())
