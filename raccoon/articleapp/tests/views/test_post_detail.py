import datetime

from articleapp.models import Post, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone


class PostDetailViewTests(TestCase):
    def setUp(self):
        self.today_datetime = timezone.now()
        self.users = [
            User.objects.create_user(username="testuser_1", password="testuser_1"),
            User.objects.create_user(username="testuser_2", password="testuser_2"),
        ]

    def test_存在する公開中の投稿にアクセス(self):
        post = Post.objects.create(
            title="post_0_tite",
            body="post_0_body",
            user=self.users[0],
            slug="post_0_slug",
            is_published=True,
            date_publish=self.today_datetime.date(),
        )
        c = Client()
        response = c.get(
            reverse(
                "post_detail",
                kwargs={"username": self.users[0].username, "slug": "post_0_slug"},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["post"], post)
        self.assertEqual(response.context["post_user"], self.users[0])
        self.assertQuerysetEqual(response.context["other_posts"], Post.objects.none())

    def test_存在する下書き中の投稿にアクセス(self):
        Post.objects.create(
            title="post_0_tite",
            body="post_0_body",
            user=self.users[0],
            slug="post_0_slug",
            is_published=False,
            date_publish=self.today_datetime.date(),
        )
        c = Client()
        response = c.get(
            reverse(
                "post_detail",
                kwargs={"username": self.users[0].username, "slug": "post_0_slug"},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_存在するユーザーの存在しない投稿にアクセス(self):
        Post.objects.create(
            title="post_0_tite",
            body="post_0_body",
            user=self.users[0],
            slug="post_0_slug",
            is_published=True,
            date_publish=self.today_datetime.date(),
        )
        Post.objects.create(
            title="post_1_tite",
            body="post_1_body",
            user=self.users[1],
            slug="post_1_slug",
            is_published=True,
            date_publish=self.today_datetime.date(),
        )
        c = Client()
        response = c.get(
            reverse(
                "post_detail",
                kwargs={"username": self.users[1].username, "slug": "post_0_slug"},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_存在しないユーザーの投稿にアクセス(self):
        Post.objects.create(
            title="post_0_tite",
            body="post_0_body",
            user=self.users[0],
            slug="post_0_slug",
            is_published=True,
            date_publish=self.today_datetime.date(),
        )
        c = Client()
        response = c.get(
            reverse(
                "post_detail",
                kwargs={"username": "testuser", "slug": "post_0_slug"},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_投稿ユーザーの他の投稿を表示(self):
        posts = [
            Post(
                title=f"post_{i}_tite",
                body=f"post_{i}_body",
                user=self.users[0],
                slug=f"post_{i}_slug",
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(0, 2)
        ]
        posts += [
            Post(
                title=f"post_{i}_tite",
                body=f"post_{i}_body",
                user=self.users[0],
                slug=f"post_{i}_slug",
                is_published=False,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(2, 4)
        ]
        posts += [
            Post(
                title=f"post_{i}_tite",
                body=f"post_{i}_body",
                user=self.users[0],
                slug=f"post_{i}_slug",
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(4, 10)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        response = c.get(
            reverse(
                "post_detail",
                kwargs={"username": self.users[0].username, "slug": "post_7_slug"},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["post"], posts[7])
        self.assertEqual(response.context["post_user"], self.users[0])
        self.assertListEqual(
            list(response.context["other_posts"]), posts[0:2] + posts[4:7]
        )
