import datetime
import random

from articleapp.models import Post, Tag, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone


class IndexViewTests(TestCase):
    def setUp(self):
        self.today_datetime = timezone.now()
        self.number_of_posts = 5
        self.number_of_tags = 10

    def test_トップページにアクセス_新着記事とタグを最大件数表示(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        posts = [
            Post(
                title=f"post_{i + 1}",
                body=f"post_{i + 1}_body",
                user=user,
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(self.number_of_posts + 10)
        ]
        Post.objects.bulk_create(posts)
        tags = [Tag(name=f"tag_{i + 1}") for i in range(self.number_of_tags + 10)]
        Tag.objects.bulk_create(tags)

        # 全てのタグを何らかの記事に紐づけておく。
        for tag in tags:
            random.choice(posts).tags.add(tag)

        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["posts"]), posts[0 : self.number_of_posts]
        )
        self.assertEqual(len(response.context["tags"]), self.number_of_tags)

    def test_投稿が表示件数より少ない(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        posts = [
            Post(
                title=f"post_{i + 1}",
                body=f"post_{i + 1}_body",
                user=user,
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(self.number_of_posts - 1)
        ]
        Post.objects.bulk_create(posts)
        tags = [Tag(name=f"tag_{i + 1}") for i in range(20)]
        Tag.objects.bulk_create(tags)

        # 全てのタグを何らかの記事に紐づけておく。
        for tag in tags:
            random.choice(posts).tags.add(tag)

        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["posts"]), posts)
        self.assertEqual(len(response.context["tags"]), self.number_of_tags)

    def test_タグが表示件数より少ない(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        posts = [
            Post(
                title=f"post_{i + 1}",
                body=f"post_{i + 1}_body",
                user=user,
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(self.number_of_posts)
        ]
        Post.objects.bulk_create(posts)
        tags = [Tag(name=f"tag_{i + 1}") for i in range(self.number_of_tags - 1)]
        Tag.objects.bulk_create(tags)

        # 全てのタグを何らかの記事に紐づけておく。
        for tag in tags:
            random.choice(posts).tags.add(tag)

        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["posts"]), posts[0 : self.number_of_posts]
        )
        self.assertEqual(len(response.context["tags"]), self.number_of_tags - 1)

    def test_公開中の投稿のみが表示される(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        posts = [
            Post(
                title="post_1",
                body="post_1_body",
                user=user,
                is_published=True,
                date_publish=(self.today_datetime.date()),
            ),
            Post(
                title="post_2",
                body="post_2_body",
                user=user,
                is_published=False,
                date_publish=(self.today_datetime.date()),
            ),
        ]
        Post.objects.bulk_create(posts)
        tags = [Tag(name=f"tag_{i + 1}") for i in range(self.number_of_tags + 10)]
        Tag.objects.bulk_create(tags)

        # 全てのタグを公開中の記事に紐づけておく。
        for tag in tags:
            posts[0].tags.add(tag)

        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["posts"]), [posts[0]])
        self.assertEqual(len(response.context["tags"]), self.number_of_tags)

    def test_投稿が無いまたは下書き投稿のみタグは表示されない(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        tags = [Tag(name=f"tag_{i + 1}") for i in range(3)]
        Tag.objects.bulk_create(tags)
        posts = [
            Post(
                title="post_1",
                body="post_1_body",
                user=user,
                is_published=True,
                date_publish=(self.today_datetime.date()),
            ),
            Post(
                title="post_2",
                body="post_2_body",
                user=user,
                is_published=False,
                date_publish=(self.today_datetime.date()),
            ),
        ]
        Post.objects.bulk_create(posts)
        posts[0].tags.add(tags[0])
        posts[1].tags.add(tags[1])

        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["posts"]), [posts[0]])
        self.assertEqual(list(response.context["tags"]), [tags[0]])

    def test_タグが重複して表示されないこと(self):
        user = User.objects.create_user(username="testuser", password="testuser")
        tags = [Tag(name=f"tag_{i}") for i in range(3)]
        Tag.objects.bulk_create(tags)
        posts = [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=user,
                is_published=True,
                date_publish=self.today_datetime.date(),
            )
            for i in range(self.number_of_posts)
        ]
        Post.objects.bulk_create(posts)
        for post in posts:
            post.tags.add(tags[0])
        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(list(response.context["tags"]), [tags[0]])
