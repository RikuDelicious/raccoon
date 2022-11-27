import datetime
import random

from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy
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


class SearchViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser_1", password="testuser_1")
        self.users = [user]
        self.url_path = reverse_lazy("search")
        self.today_datetime = timezone.now()
        self.date_format = "%Y-%m-%d"

    def test_投稿無しでページアクセス(self):
        c = Client()
        response = c.get(self.url_path)
        self.assertEqual(response.status_code, 200)

    def test_投稿ありでページアクセス(self):
        tags = [Tag(name=f"tag_{i}") for i in range(10)]
        Tag.objects.bulk_create(tags)
        posts = [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date()),
            )
            for i in range(10)
        ]
        Post.objects.bulk_create(posts)
        for post in posts:
            post.tags.add(random.choice(tags))
        c = Client()
        response = c.get(self.url_path)
        self.assertEqual(response.status_code, 200)

    def test_フィルタ_タグ(self):
        tags = [Tag(name=f"tag_{i}") for i in range(3)]
        Tag.objects.bulk_create(tags)
        posts = [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date()),
            )
            for i in range(10)
        ]
        Post.objects.bulk_create(posts)
        for post in posts[0:3]:
            post.tags.add(tags[0])

        for post in posts[3:6]:
            post.tags.add(tags[1])

        for post in posts[6:10]:
            post.tags.add(tags[0], tags[1])

        c = Client()
        response = c.get(self.url_path, {"tags": ["tag_0"]})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list),
            posts[0:3] + posts[6:10],
        )

        response = c.get(self.url_path, {"tags": ["tag_1"]})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[3:10]
        )

        response = c.get(self.url_path, {"tags": ["tag_0", "tag_1"]})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[6:10]
        )

        response = c.get(self.url_path, {"tags": ["tag_2"]})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["post_list_page"].object_list, Post.objects.none()
        )

        response = c.get(self.url_path, {"tags": ["tag_0", "tag_1", "tag_2"]})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["post_list_page"].object_list, Post.objects.none()
        )

    def test_フィルタ_期間(self):
        posts = [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(10)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        start_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-7))
        ).strftime(self.date_format)
        response = c.get(self.url_path, {"period_start_date": start_date})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:8]
        )

        end_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-2))
        ).strftime(self.date_format)
        response = c.get(self.url_path, {"period_end_date": end_date})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[2:]
        )

        start_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-7))
        ).strftime(self.date_format)
        end_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-2))
        ).strftime(self.date_format)
        response = c.get(
            self.url_path,
            {"period_start_date": start_date, "period_end_date": end_date},
        )
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[2:8]
        )

        start_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-5))
        ).strftime(self.date_format)
        end_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-5))
        ).strftime(self.date_format)
        response = c.get(
            self.url_path,
            {"period_start_date": start_date, "period_end_date": end_date},
        )
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[5]]
        )

        start_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-2))
        ).strftime(self.date_format)
        end_date = (
            self.today_datetime.date() + datetime.timedelta(days=(-7))
        ).strftime(self.date_format)
        response = c.get(
            self.url_path,
            {"period_start_date": start_date, "period_end_date": end_date},
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["post_list_page"].object_list, Post.objects.none()
        )

    def test_フィルタ_キーワード(self):
        posts = [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(10)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        response = c.get(self.url_path, {"keyword": "post_5_タイトル"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[5]]
        )

        response = c.get(self.url_path, {"keyword": "_5_タイ"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[5]]
        )

        response = c.get(self.url_path, {"keyword": "post_5_body_本文"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[5]]
        )

        response = c.get(self.url_path, {"keyword": "_5_body_本"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[5]]
        )

        response = c.get(self.url_path, {"keyword": "_5_"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[5]]
        )

        response = c.get(self.url_path, {"keyword": "post_"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts
        )

    def test_フィルタ_並び順(self):
        posts = [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(10)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        response = c.get(self.url_path)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts
        )

        response = c.get(self.url_path, {"sort": "date_publish_desc"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts
        )

        response = c.get(self.url_path, {"sort": "date_publish_asc"})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), list(reversed(posts))
        )

    def test_ページネーション(self):
        posts = [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(21)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        response = c.get(self.url_path)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:10]
        )

        response = c.get(self.url_path, {"page": 1})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:10]
        )

        response = c.get(self.url_path, {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[10:20]
        )

        response = c.get(self.url_path, {"page": 3})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[20]]
        )

        response = c.get(self.url_path, {"page": 4})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[20]]
        )
        self.assertEqual(response.context["post_list_page"].number, 3)

        response = c.get(self.url_path, {"page": 0})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[20]]
        )
        self.assertEqual(response.context["post_list_page"].number, 3)

    def test_公開中の投稿のみが表示される(self):
        posts = [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(0, 5)
        ]
        posts += [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                user=self.users[0],
                is_published=False,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(5, 10)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        response = c.get(self.url_path)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:5]
        )

    def test_ページネーション_ナビゲーション(self):
        """
        ページネーションのナビゲーションに表示するページ番号を決めるロジックのテスト
        """
        posts = [
            Post(
                title=f"post_{i}_タイトル",
                body=f"post_{i}_body_本文",
                user=self.users[0],
                is_published=True,
                date_publish=self.today_datetime.date(),
            )
            for i in range(0, 10)
        ]

        c = Client()

        # 投稿無し
        response = c.get(self.url_path, {"paginate_by": 1})
        context = {"numbers": [1], "display_first": False, "display_last": False}
        self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が1ページのみ
        Post.objects.bulk_create([posts[0]])
        response = c.get(self.url_path, {"paginate_by": 1})
        context = {"numbers": [1], "display_first": False, "display_last": False}
        self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が4
        Post.objects.bulk_create(posts[1:4])
        for i in range(1, 5):
            response = c.get(self.url_path, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [1, 2, 3, 4],
                "display_first": False,
                "display_last": False,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が5
        Post.objects.bulk_create([posts[4]])
        for i in range(1, 6):
            response = c.get(self.url_path, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [1, 2, 3, 4, 5],
                "display_first": False,
                "display_last": False,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が6
        Post.objects.bulk_create([posts[5]])
        # 1 ~ 3 ページ目まで
        for i in range(1, 4):
            response = c.get(self.url_path, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [1, 2, 3, 4],
                "display_first": False,
                "display_last": True,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)
        # 4 ~ 6ページ目
        for i in range(4, 6):
            response = c.get(self.url_path, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [3, 4, 5, 6],
                "display_first": True,
                "display_last": False,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が10
        Post.objects.bulk_create(posts[6:10])
        # 1 ~ 3 ページ目まで
        for i in range(1, 4):
            response = c.get(self.url_path, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [1, 2, 3, 4],
                "display_first": False,
                "display_last": True,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)
        # 4 ~ 7 ページ目まで
        for i in range(4, 8):
            response = c.get(self.url_path, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [i - 1, i, i + 1],
                "display_first": True,
                "display_last": True,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)
        # 8 ~ 10 ページ目まで
        for i in range(8, 11):
            response = c.get(self.url_path, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [7, 8, 9, 10],
                "display_first": True,
                "display_last": False,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)


class SearchTagsViewTests(TestCase):
    def setUp(self):
        self.url_path = reverse_lazy("search_tags")

    def test_タグ検索(self):
        tags = [Tag(name=f"tag_{i}_タグ{i}") for i in range(20)]
        tags = Tag.objects.bulk_create(tags)
        tags = [{"id": tag.id, "name": tag.name} for tag in tags]

        c = Client()
        # クエリパラメータ無し
        response = c.get(self.url_path)
        self.assertListEqual(response.json()["tags"], tags)
        # キーワード空文字
        response = c.get(self.url_path, {"keyword": ""})
        self.assertListEqual(response.json()["tags"], tags)
        # 完全一致
        response = c.get(self.url_path, {"keyword": "tag_1_タグ1"})
        self.assertListEqual(response.json()["tags"], [tags[1]])
        # 大文字小文字を区別しない
        response = c.get(self.url_path, {"keyword": "TAG_1_タグ1"})
        self.assertListEqual(response.json()["tags"], [tags[1]])
        # 部分一致
        response = c.get(self.url_path, {"keyword": "ag_1"})
        self.assertListEqual(response.json()["tags"], [tags[1]] + tags[10:20])


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
