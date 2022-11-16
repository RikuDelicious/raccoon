import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post, Tag, User


# Create your tests here.
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

        c = Client()
        response = c.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["posts"]), [posts[0]])
        self.assertEqual(len(response.context["tags"]), self.number_of_tags)
