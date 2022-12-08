import datetime

from articleapp.models import Post, User
from django.test import Client, TestCase
from django.utils import timezone


class PostTests(TestCase):
    def setUp(self):
        self.today_datetime = timezone.now()

    def test_publishメソッド_下書き状態の投稿を公開(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        post = Post.objects.create(title="タイトル", body="本文", user=user)

        # 投稿はデフォルトでは下書き状態
        self.assertEqual(post.is_published, False)
        self.assertEqual(post.date_publish, None)

        post.publish()
        self.assertEqual(post.is_published, True)
        self.assertEqual(post.date_publish, self.today_datetime.date())

    def test_publishメソッド_既に公開中の投稿で呼び出し(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        date_publish = self.today_datetime.date() - datetime.timedelta(days=5)
        post = Post.objects.create(
            title="タイトル",
            body="本文",
            user=user,
            is_published=True,
            date_publish=date_publish,
        )

        # publishメソッドを呼び出しても投稿日は更新されない
        post.publish()
        self.assertEqual(post.is_published, True)
        self.assertEqual(post.date_publish, date_publish)

    def test_get_absolute_urlメソッド(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        post = Post.objects.create(
            title="タイトル",
            body="本文",
            user=user,
            is_published=True,
            date_publish=self.today_datetime.date(),
        )

        url = post.get_absolute_url()
        c = Client()
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
