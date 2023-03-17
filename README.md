# アプリケーションの概要
誰でもユーザー登録して記事を投稿できるという簡易Webサービスとなります。  
Python + Djangoを使って開発しております。  
![top](https://user-images.githubusercontent.com/101910815/225845482-765cc981-b580-4521-9e54-68c1304ea18c.png)


トップページの画面右上の「新規登録」からユーザー登録後、  
画面右上の部分がユーザーアイコンに変わりますので、  
そちらをクリックし、「新規投稿」から記事投稿を行うことが出来ます。  

投稿した記事は一覧画面やマイページに表示され、検索することも可能となります。  

**※一部、未完成の箇所があり、以下の箇所については開発中となります。**
- デフォルトユーザー
- 記事詳細本文のデザイン
- 記事を投稿するエディタ


# データベースのテーブル設計
Djangoプロジェクト内の以下のファイルにてテーブルを定義しております。
```
リポジトリのルート/raccoon/articleapp/models.py
```

上記ファイル内でUserテーブル、Postテーブル、Tagテーブルを定義し、
ER図は以下のようになります。
![er](https://user-images.githubusercontent.com/101910815/225845373-256dacd2-6790-4636-bdc7-e1ee420cc1d2.png)

該当コード(※テーブル定義以外のコードについては省略)
```python
class User(AbstractUser):
    display_name = models.CharField(
        max_length=100, null=True, verbose_name="ニックネーム", blank=True
    )
    profile_image = models.ImageField(
        upload_to="uploads/", null=True, verbose_name="プロフィール画像", blank=True
    )

    username_validator = ASCIIUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    class Meta(AbstractUser.Meta):
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="タイトル")
    body = models.TextField(verbose_name="本文", blank=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    slug = models.SlugField(default=generate_random_slug, verbose_name="スラッグ")
    tags = models.ManyToManyField(to="Tag", blank=True, verbose_name="タグ")
    is_published = models.BooleanField(default=False)
    date_publish = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_publish", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "slug"], name="unique_user_slug"),
        ]
        verbose_name = "投稿"
        verbose_name_plural = "投稿"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "タグ"
        verbose_name_plural = "タグ"
```

基本的には以下の要件を満たすテーブル・リレーション設計となっております。  
- ユーザー登録が可能である
- ユーザーが記事を投稿し、記事とユーザーが紐づけられる
- 記事にタグを登録し手紐づけ、タグによる記事検索が可能である


リレーションの設定としては、
- ユーザーテーブルと記事テーブルが1対多の関係
- 記事テーブルとタグテーブルが多対多の関係

となっております。

また、実際にタグで記事を検索する際には想定と異なる結果になるという注意点があり、  
そちらについては以下の記事を作成して検討いたしました（私が書いた記事となります）。  
https://qiita.com/rikudelicious/items/f7bf61dcaa6149ad9931


# 開発を始めるまでの準備
本リポジトリをClone後、実際に開発サーバーを立ち上げてサイトを確認するまでの手順をご説明します。

### 1.pythonの仮想環境を立ち上げ、必要なパッケージをインストールする
本アプリケーションはpython3.11で動作することを確認しています。

**pythonの仮想環境を立ち上げて有効化する**  
Windows(Pyランチャー)の場合
```
$ /path/to/repository> py -3.11 -m venv venv
$ /path/to/repository> .\venv\Scripts\Activate.ps1
```
Linuxの場合
```
$ /path/to/repository> python -m venv venv
$ /path/to/repository> . ./venv/bin/activate
```

**必要なpythonパッケージをインストールする**  
```
(venv)$ /path/to/repository> cd ./raccoon
(venv)$ /path/to/repository/raccoon> pip install -r ./requirements.txt
```

### 2.データベースのマイグレーションコマンドを実行する
開発環境ではSQLiteを利用するため、SQLiteのデータベースを初期化します。
```
(venv)$ /path/to/repository/raccoon> python ./manage.py migrate
```

また、管理画面のスーパーユーザーを作成するには以下のコマンドを実行します。  
管理画面は`/admin`にてアクセスすることが出来ます。
```
(venv)$ /path/to/repository/raccoon> python ./manage.py createsuperuser
```

### 3.開発サーバーを立ち上げる
準備が整ったので、開発サーバーを立ち上げます。  
以下のコマンドを実行します。
```
(venv)$ /path/to/repository/raccoon> python ./manage.py runserver
```

成功すると以下のような表示が出ます。
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March xx, 2023 - xx:xx:xx
Django version 4.1.3, using settings 'raccoon.settings.development'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

この状態で、「Starting development server at...」の後に記載されているURLにアクセスすることで、  
開発中のサイトにアクセスすることが出来ます。
