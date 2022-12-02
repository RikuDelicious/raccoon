from pathlib import Path

from articleapp import tests
from articleapp.forms import AccountUpdateForm, ProfileUpdateForm
from articleapp.models import User
from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse_lazy
import filecmp


class UserSettingsTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(username=f"testuser_{i}", password=f"testuser_{i}")
            for i in range(4)
        ]

        # プロフィール画像設定
        profile_image_path = (
            Path(tests.__path__[0]) / "sample_files" / "profile_image.png"
        )
        with profile_image_path.open(mode="rb") as f:
            profile_image_file = File(f)
            self.users[1].profile_image.save(
                f"testuser_1_profile_image{profile_image_path.suffix}",
                profile_image_file,
            )
            self.users[3].profile_image.save(
                f"testuser_3_profile_image{profile_image_path.suffix}",
                profile_image_file,
            )

        # ニックネーム設定
        self.users[2].display_name = "テストユーザー２"
        self.users[2].save()
        self.users[3].display_name = "テストユーザー３"
        self.users[3].save()

        self.url_user_settings = reverse_lazy("user_settings")
        self.url_user_settings_profile = reverse_lazy("user_settings_profile")
        self.url_user_settings_account = reverse_lazy("user_settings_account")

    def test_デフォルトurlで設定ページにアクセスするとリダイレクト(self):
        c = Client()

        # 未ログインはログインページにリダイレクト
        response = c.get(self.url_user_settings, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "login")

        # ログイン済み
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url_user_settings)
        # プロフィール更新ページにリダイレクト
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], self.url_user_settings_profile)

    def test_プロフィール更新ページにアクセス(self):
        c = Client()

        # 未ログインはログインページにリダイレクト
        response = c.get(self.url_user_settings_profile, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "login")

        # ログイン済み
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            response = c.get(self.url_user_settings_profile)
            self.assertEqual(response.status_code, 200)
            # 現在のメニューのチェック
            self.assertEqual(response.context["current_menu_item"], "profile")
            # メニューアイテムのチェック
            self.assertListEqual(
                response.context["menu_items"],
                [
                    {
                        "name": "profile",
                        "label": "プロフィール",
                        "url_name": "user_settings_profile",
                    },
                    {
                        "name": "account",
                        "label": "アカウント情報",
                        "url_name": "user_settings_account",
                    },
                ],
            )
            # フォームのチェック
            self.assertIsInstance(response.context["form"], ProfileUpdateForm)
            self.assertEqual(response.context["form"].is_bound, False)
            self.assertEqual(response.context["form"].instance, self.users[i])
            self.assertEqual(
                response.context["form"].initial["display_name"],
                self.users[i].display_name,
            )
            self.assertEqual(
                response.context["form"].initial["profile_image"] or None,
                self.users[i].profile_image or None,
            )

    def test_アカウント情報ページにアクセス(self):
        c = Client()

        # 未ログインはログインページにリダイレクト
        response = c.get(self.url_user_settings_account, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "login")

        # ログイン済み
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            response = c.get(self.url_user_settings_account)
            self.assertEqual(response.status_code, 200)
            # 現在のメニューのチェック
            self.assertEqual(response.context["current_menu_item"], "account")
            # メニューアイテムのチェック
            self.assertListEqual(
                response.context["menu_items"],
                [
                    {
                        "name": "profile",
                        "label": "プロフィール",
                        "url_name": "user_settings_profile",
                    },
                    {
                        "name": "account",
                        "label": "アカウント情報",
                        "url_name": "user_settings_account",
                    },
                ],
            )
            # フォームのチェック
            self.assertIsInstance(response.context["form"], AccountUpdateForm)
            self.assertEqual(response.context["form"].is_bound, False)
            self.assertEqual(response.context["form"].instance, self.users[i])
            self.assertEqual(
                response.context["form"].initial["username"], self.users[i].username
            )

    def test_プロフィール更新_変更なし(self):
        c = Client()
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            response = c.get(self.url_user_settings_profile)
            form = response.context["form"]
            post_data = {}

            if form.initial["display_name"] is not None:
                post_data["display_name"] = form.initial["display_name"]

            # profile_imageフィールドは変更しない場合ファイルを送信しない
            response = c.post(self.url_user_settings_profile, post_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers["Location"], self.url_user_settings_profile
            )

            # フォーム送信後のユーザー情報の確認
            user = User.objects.get(pk=self.users[i].id)
            self.assertEqual(user.display_name, form.initial["display_name"])
            self.assertEqual(
                user.profile_image or None, form.initial["profile_image"] or None
            )

    def test_プロフィール更新_ニックネームのみ変更(self):
        c = Client()
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            response = c.get(self.url_user_settings_profile)
            form = response.context["form"]
            post_data = {}

            # ニックネームを変更
            post_data["display_name"] = f"テストユーザー{i}_変更後"

            # profile_imageフィールドは変更しない場合ファイルを送信しない
            response = c.post(self.url_user_settings_profile, post_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers["Location"], self.url_user_settings_profile
            )

            # フォーム送信後のユーザー情報の確認
            user = User.objects.get(pk=self.users[i].id)
            self.assertEqual(user.display_name, post_data["display_name"])
            self.assertEqual(
                user.profile_image or None, form.initial["profile_image"] or None
            )

    def test_プロフィール更新_プロフィール画像のみ変更(self):
        c = Client()
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            response = c.get(self.url_user_settings_profile)
            form = response.context["form"]
            post_data = {}

            if form.initial["display_name"] is not None:
                post_data["display_name"] = form.initial["display_name"]

            # 新規プロフィール画像読み込み
            upload_image_path = (
                Path(tests.__path__[0]) / "sample_files" / "profile_image_new.png"
            )
            with upload_image_path.open("rb") as f:
                # フォーム送信
                post_data["profile_image"] = f
                response = c.post(self.url_user_settings_profile, post_data)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.headers["Location"], self.url_user_settings_profile
                )

                # フォーム送信後のユーザー情報の確認
                user = User.objects.get(pk=self.users[i].id)
                self.assertEqual(user.display_name, form.initial["display_name"])
                self.assertIsNotNone(user.profile_image or None)
                # ユーザーのプロフィール画像がアップロードした画像ファイルと同じであることを確認
                self.assertTrue(
                    filecmp.cmp(user.profile_image.path, upload_image_path),
                    msg="フォーム送信後のユーザーのプロフィール画像が期待値と異なります",
                )

    def test_プロフィール更新_ニックネームとプロフィール画像を変更(self):
        c = Client()
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            post_data = {}

            # ニックネームを変更
            post_data["display_name"] = f"テストユーザー{i}_変更後"

            # 新規プロフィール画像読み込み
            upload_image_path = (
                Path(tests.__path__[0]) / "sample_files" / "profile_image_new.png"
            )
            with upload_image_path.open("rb") as f:
                # フォーム送信
                post_data["profile_image"] = f
                response = c.post(self.url_user_settings_profile, post_data)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.headers["Location"], self.url_user_settings_profile
                )

                # フォーム送信後のユーザー情報の確認
                user = User.objects.get(pk=self.users[i].id)
                self.assertEqual(user.display_name, post_data["display_name"])
                self.assertIsNotNone(user.profile_image or None)
                # ユーザーのプロフィール画像がアップロードした画像ファイルと同じであることを確認
                self.assertTrue(
                    filecmp.cmp(user.profile_image.path, upload_image_path),
                    msg="フォーム送信後のユーザーのプロフィール画像が期待値と異なります",
                )

    def test_プロフィール更新_プロフィール画像を削除(self):
        c = Client()
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            post_data = {"profile_image-clear": True}

            response = c.post(self.url_user_settings_profile, post_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers["Location"], self.url_user_settings_profile
            )

            # ユーザーのプロフィール画像が削除されていることの確認
            user = User.objects.get(pk=self.users[i].id)
            self.assertIsNone(user.profile_image or None)

    def test_プロフィール更新_エラーでページ再表示(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        response = c.get(self.url_user_settings_profile)
        form = response.context["form"]
        # 最大文字数を越えるニックネームを送信する
        display_name = "".join(
            ["あ" for i in range(form.fields["display_name"].max_length + 1)]
        )
        response = c.post(
            self.url_user_settings_profile, {"display_name": display_name}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.resolver_match.url_name, "user_settings_profile")
        self.assertNotEqual(response.context["form"].errors.as_data(), {})
        self.assertFalse(User.objects.filter(display_name=display_name).exists())

    def test_アカウント情報_変更なしで送信(self):
        c = Client()
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            response = c.get(self.url_user_settings_account)
            form = response.context["form"]
            post_data = {"username": form.initial["username"]}

            response = c.post(self.url_user_settings_account, post_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers["Location"], self.url_user_settings_account
            )

            # フォーム送信後のユーザー情報の確認
            user = User.objects.get(pk=self.users[i].id)
            self.assertEqual(user.username, form.initial["username"])

    def test_アカウント情報_ユーザー名変更(self):
        c = Client()
        for i in range(len(self.users)):
            c.login(username=f"testuser_{i}", password=f"testuser_{i}")
            response = c.get(self.url_user_settings_account)
            form = response.context["form"]
            post_data = {"username": f"testuser_{i}_new"}

            response = c.post(self.url_user_settings_account, post_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.headers["Location"], self.url_user_settings_account
            )

            # フォーム送信後のユーザー情報の確認
            user = User.objects.get(pk=self.users[i].id)
            self.assertEqual(user.username, post_data["username"])

    def test_アカウント情報_エラーでページ再表示(self):
        c = Client()
        c.login(username="testuser_0", password="testuser_0")
        # ascii文字以外のusernameを送信する
        username = "あいうえおかきくけこ"
        response = c.post(self.url_user_settings_account, {"username": username})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.resolver_match.url_name, "user_settings_account")
        self.assertNotEqual(response.context["form"].errors.as_data(), {})
        self.assertFalse(User.objects.filter(username=username).exists())
