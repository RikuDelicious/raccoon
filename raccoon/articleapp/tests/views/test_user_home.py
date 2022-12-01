import datetime

from articleapp.models import Post, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone


class UserHomeViewTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(username="testuser_0", password="testuser_0"),
            User.objects.create_user(username="testuser_1", password="testuser_1"),
        ]
        self.today_datetime = timezone.now()

    def test_存在するユーザーのページにアクセス(self):
        c = Client()

        # 未ログインでアクセス
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.status_code, 200)

        # ログイン済み&ページのユーザーとは異なるユーザーでアクセス
        c.login(username="testuser_1", password="testuser_1")
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.status_code, 200)

        # ログイン済み&ページのユーザーと同じユーザーでアクセス
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[1].username})
        )
        self.assertEqual(response.status_code, 200)

    def test_存在するユーザーの下書き一覧にアクセス(self):
        c = Client()

        # 未ログインでアクセス
        response = c.get(
            reverse("user_home_drafts", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            reverse("user_home", kwargs={"username": self.users[0].username}),
        )

        # ログイン済み&ページのユーザーとは異なるユーザーでアクセス
        c.login(username="testuser_1", password="testuser_1")
        response = c.get(
            reverse("user_home_drafts", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            reverse("user_home", kwargs={"username": self.users[0].username}),
        )

        # ログイン済み&ページのユーザーと同じユーザーでアクセス
        response = c.get(
            reverse("user_home_drafts", kwargs={"username": self.users[1].username})
        )
        self.assertEqual(response.status_code, 200)

    def test_存在しないユーザーのページにアクセス(self):
        c = Client()
        response = c.get(reverse("user_home", kwargs={"username": "unknownuser"}))
        self.assertEqual(response.status_code, 404)

        response = c.get(
            reverse("user_home_drafts", kwargs={"username": "unknownuser"})
        )
        self.assertEqual(response.status_code, 404)

    def test_urlで指定したユーザーの情報取得(self):
        c = Client()
        # 通常のユーザーページ
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.context["user_to_display"], self.users[0])

        # 下書き一覧
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(
            reverse("user_home_drafts", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.context["user_to_display"], self.users[0])

    def test_閲覧ユーザーとページのユーザーが同じかどうかをコンテキストに保持(self):
        c = Client()

        # 未ログイン
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.context["is_logged_in_user_home"], False)

        # ログイン済み&ページのユーザーとは異なるユーザー
        c.login(username="testuser_1", password="testuser_1")
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username})
        )
        self.assertEqual(response.context["is_logged_in_user_home"], False)

        # ログイン済み&ページのユーザーと同じユーザーでアクセス
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[1].username})
        )
        self.assertEqual(response.context["is_logged_in_user_home"], True)

        # ログイン済み&ページのユーザーと同じユーザーで下書き一覧にアクセス
        response = c.get(
            reverse("user_home_drafts", kwargs={"username": self.users[1].username})
        )
        self.assertEqual(response.context["is_logged_in_user_home"], True)

    def test_ユーザーの投稿を取得(self):
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
        posts += [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[1],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(10, 20)
        ]
        posts += [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=False,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(20, 30)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        # 通常のユーザーページ
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username})
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:10]
        )

        # 下書き一覧
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(
            reverse("user_home_drafts", kwargs={"username": self.users[0].username})
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[20:30]
        )

    def test_通常のユーザーページは下書き状態の投稿は表示しない(self):
        posts = [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(5)
        ]
        posts += [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=False,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(5, 10)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username})
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:5]
        )

    def test_下書き一覧では公開中の投稿は表示しない(self):
        posts = [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=True,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(5)
        ]
        posts += [
            Post(
                title=f"post_{i}",
                body=f"post_{i}_body",
                user=self.users[0],
                is_published=False,
                date_publish=(self.today_datetime.date() - datetime.timedelta(days=i)),
            )
            for i in range(5, 10)
        ]
        Post.objects.bulk_create(posts)

        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(
            reverse("user_home_drafts", kwargs={"username": self.users[0].username})
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[5:10]
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
        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username}),
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:10]
        )

        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username}),
            {"page": 1},
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[0:10]
        )

        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username}),
            {"page": 2},
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), posts[10:20]
        )

        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username}),
            {"page": 3},
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[20]]
        )

        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username}),
            {"page": 4},
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[20]]
        )
        self.assertEqual(response.context["post_list_page"].number, 3)

        response = c.get(
            reverse("user_home", kwargs={"username": self.users[0].username}),
            {"page": 0},
        )
        self.assertListEqual(
            list(response.context["post_list_page"].object_list), [posts[20]]
        )
        self.assertEqual(response.context["post_list_page"].number, 3)

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
        url = reverse("user_home", kwargs={"username": self.users[0].username})

        # 投稿無し
        response = c.get(url, {"paginate_by": 1})
        context = {"numbers": [1], "display_first": False, "display_last": False}
        self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が1ページのみ
        Post.objects.bulk_create([posts[0]])
        response = c.get(url, {"paginate_by": 1})
        context = {"numbers": [1], "display_first": False, "display_last": False}
        self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が4
        Post.objects.bulk_create(posts[1:4])
        for i in range(1, 5):
            response = c.get(url, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [1, 2, 3, 4],
                "display_first": False,
                "display_last": False,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)

        # ページ数が5
        Post.objects.bulk_create([posts[4]])
        for i in range(1, 6):
            response = c.get(url, {"paginate_by": 1, "page": i})
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
            response = c.get(url, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [1, 2, 3, 4],
                "display_first": False,
                "display_last": True,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)
        # 4 ~ 6ページ目
        for i in range(4, 6):
            response = c.get(url, {"paginate_by": 1, "page": i})
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
            response = c.get(url, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [1, 2, 3, 4],
                "display_first": False,
                "display_last": True,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)
        # 4 ~ 7 ページ目まで
        for i in range(4, 8):
            response = c.get(url, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [i - 1, i, i + 1],
                "display_first": True,
                "display_last": True,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)
        # 8 ~ 10 ページ目まで
        for i in range(8, 11):
            response = c.get(url, {"paginate_by": 1, "page": i})
            context = {
                "numbers": [7, 8, 9, 10],
                "display_first": True,
                "display_last": False,
            }
            self.assertDictEqual(response.context["post_list_pagination_nav"], context)
