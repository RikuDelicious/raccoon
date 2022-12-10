import string
import random
from urllib.parse import urlparse

from articleapp.forms import PostForm
from articleapp.models import Post, Tag, User
from django.test import Client, TestCase
from django.urls import reverse
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

    def test_エラーでページ再表示(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        # フォーム取得
        response = c.get(self.url)
        form = response.context["form"]

        # フォーム送信
        post_data = {
            # titleフィールドを除外
            "tags_text": "Python Django",
            "slug": form.get_initial_for_field(form.fields["slug"], "slug"),
            "body": "投稿本文",
            "save_option": "save_and_publish",
        }
        response = c.post(self.url, post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertIsNot(response.context["form"].errors.as_data, {})
        self.assertFalse(
            Post.objects.filter(user=self.users[0], slug=post_data["slug"]).exists()
        )

    def test_フォーム_titleフィールド(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        # 入力パターン
        seed = string.ascii_lowercase
        titles = [
            "",  # 空
            "a",  # 1文字
            "".join(
                random.choices(seed, k=Post._meta.get_field("title").max_length)
            ),  # 最大文字数
            "".join(
                random.choices(seed, k=(Post._meta.get_field("title").max_length + 1))
            ),  # 最大文字数 + 1
        ]

        for i, title in enumerate(titles):
            # フォーム取得
            response = c.get(self.url)
            form = response.context["form"]

            # フォーム送信
            post_data = {
                "title": title,
                "tags_text": "Python Django",
                "slug": form.get_initial_for_field(form.fields["slug"], "slug"),
                "body": "投稿本文",
                "save_option": "save_and_publish",
            }
            response = c.post(self.url, post_data)
            if i in [0, 3]:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 302)
                redirect_url = urlparse(response.headers["Location"])
                self.assertEqual(
                    redirect_url.path,
                    reverse("user_home", kwargs={"username": "testuser_0"}),
                )

    def test_フォーム_tags_textフィールド(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        # 入力パターン
        seed = string.ascii_lowercase
        # フィールドの最大文字数のテキスト
        field_max_length_text = [
            "あ" if i % 2 == 0 else " "
            for i in range(PostForm().fields["tags_text"].max_length)
        ]
        if field_max_length_text[-1] == " ":
            field_max_length_text[-1] = "あ"
        # フィールドの最大文字数 + 1のテキスト
        field_over_max_length_text = [
            "あ" if i % 2 == 0 else " "
            for i in range(PostForm().fields["tags_text"].max_length + 1)
        ]
        if field_over_max_length_text[-1] == " ":
            field_over_max_length_text[-1] = "あ"

        tags_text_list = [
            "",  # 空
            "a",  # 1文字
            "C# .Net",  # 複数のタグ
            "C# .Net",  # 生成済みのタグ
            ".Net C# WPF",  # 生成済みのタグ + 新規タグ
            "".join(
                random.choices(seed, k=Tag._meta.get_field("name").max_length)
            ),  # タグの最大文字数
            "".join(
                random.choices(seed, k=(Tag._meta.get_field("name").max_length + 1))
            ),  # タグの最大文字数 + 1
            "".join(field_max_length_text),  # フォームの最大文字数
            "".join(field_over_max_length_text),  # フォームの最大文字数 + 1
            "JavaScript JavaScript JavaScript",  # 同じタグ名を重複して入力
        ]

        for i, tags_text in enumerate(tags_text_list):
            # フォーム取得
            response = c.get(self.url)
            form = response.context["form"]

            # フォーム送信
            post_data = {
                "title": "タイトル",
                "tags_text": tags_text,
                "slug": form.get_initial_for_field(form.fields["slug"], "slug"),
                "body": "投稿本文",
                "save_option": "save_and_publish",
            }
            response = c.post(self.url, post_data)
            if i in [6, 8]:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 302)
                redirect_url = urlparse(response.headers["Location"])
                self.assertEqual(
                    redirect_url.path,
                    reverse("user_home", kwargs={"username": "testuser_0"}),
                )

                # 投稿にタグが紐づけられていることの確認
                post = Post.objects.get(user=self.users[0], slug=post_data["slug"])
                self.assertListEqual(
                    [tag.name for tag in post.tags.order_by("name").all()],
                    sorted(set(tags_text.split())),
                )

        # タグが生成されていることの確認
        self.assertEqual(Tag.objects.filter(name="C#").count(), 1)
        self.assertEqual(Tag.objects.filter(name=".Net").count(), 1)
        self.assertEqual(Tag.objects.filter(name="WPF").count(), 1)
        self.assertEqual(Tag.objects.filter(name=tags_text_list[5]).count(), 1)
        self.assertEqual(Tag.objects.filter(name=tags_text_list[6]).count(), 0)
        self.assertEqual(Tag.objects.filter(name="JavaScript").count(), 1)

    def test_フォーム_slugフィールド(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        # 入力パターン
        seed = string.ascii_lowercase + string.digits
        slugs = [
            None,  # 初期値
            "",  # 空
            "a",  # 1文字
            "a",  # 既存のスラッグと同じ値
            "".join(
                random.choices(seed, k=Post._meta.get_field("slug").max_length)
            ),  # スラッグの最大文字数
            "".join(
                random.choices(seed, k=(Post._meta.get_field("slug").max_length + 1))
            ),  # スラッグの最大文字数 + 1
        ]

        for i, slug in enumerate(slugs):
            # フォーム取得
            response = c.get(self.url)
            form = response.context["form"]

            # フォーム送信
            post_data = {
                "title": "タイトル",
                "tags_text": "Python",
                "slug": slug
                if slug is not None
                else form.get_initial_for_field(form.fields["slug"], "slug"),
                "body": "投稿本文",
                "save_option": "save_and_publish",
            }
            response = c.post(self.url, post_data)

            if i in [1, 3, 5]:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 302)
                redirect_url = urlparse(response.headers["Location"])
                self.assertEqual(
                    redirect_url.path,
                    reverse("user_home", kwargs={"username": "testuser_0"}),
                )

    def test_フォーム_bodyフィールド(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")

        # 入力パターン
        bodies = [
            "",  # 空
            "a",  # 1文字
        ]

        for i, body in enumerate(bodies):
            # フォーム取得
            response = c.get(self.url)
            form = response.context["form"]

            # フォーム送信
            post_data = {
                "title": "タイトル",
                "tags_text": "Python",
                "slug": form.get_initial_for_field(form.fields["slug"], "slug"),
                "body": body,
                "save_option": "save_and_publish",
            }
            response = c.post(self.url, post_data)

            self.assertEqual(response.status_code, 302)
            redirect_url = urlparse(response.headers["Location"])
            self.assertEqual(
                redirect_url.path,
                reverse("user_home", kwargs={"username": "testuser_0"}),
            )
