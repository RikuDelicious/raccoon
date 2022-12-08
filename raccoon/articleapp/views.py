import datetime
import random

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AccountUpdateForm, PostForm, ProfileUpdateForm, UserCreationForm
from .models import Post, Tag, User
from .utils.pagination import create_navigation_context_from_page


# Create your views here.
def index(request):
    # tagをランダムに10個取得
    tags = list(
        Tag.objects.filter(
            # 少なくとも1つ以上の投稿が公開されているタグのみにする
            post__is_published__exact=True
        ).distinct()  # 重複を除外
    )
    tags_sample = []
    random_indexes = random.sample(range(len(tags)), min([10, len(tags)]))
    for index in random_indexes:
        tags_sample.append(tags[index])

    # Postの新着5件を取得
    # デフォルトの並び順は投稿日の降順→created_atの降順
    posts = Post.objects.filter(is_published=True)[0:5]

    return render(
        request, "articleapp/index.html", {"posts": posts, "tags": tags_sample}
    )


def search(request):
    queryset = Post.objects.all()
    querydict = request.GET
    context = {}

    # フィルタ: タグ
    if "tags" in querydict:
        # 空のquerysetを生成
        posts_filtered_tags = Post.objects.none()

        # タグ名からタグのリストを生成
        tags_name = querydict.getlist("tags")
        tags = Tag.objects.filter(name__in=tags_name)
        for tag in tags:
            posts_filtered_tags = posts_filtered_tags | Post.objects.filter(tags=tag)

        posts_filtered_tags = posts_filtered_tags.annotate(
            post_count=Count("id")
        ).filter(post_count__exact=len(tags))

        queryset = posts_filtered_tags

    # フィルタ: 期間_開始
    if "period_start_date" in querydict:
        try:
            # 日本のサイトなのでJSTの日付として扱う（TIME_ZONE = "Asia/Tokyo"）
            start_date = timezone.make_aware(
                datetime.datetime.strptime(querydict["period_start_date"], "%Y-%m-%d")
            )
            queryset = queryset.filter(date_publish__gte=start_date)
        except ValueError:
            # datetimeに変換できない値はスルー
            pass

    # フィルタ:期間_終了
    if "period_end_date" in querydict:
        try:
            # 日本のサイトなのでJSTの日付として扱う（TIME_ZONE = "Asia/Tokyo"）
            end_date = timezone.make_aware(
                datetime.datetime.strptime(querydict["period_end_date"], "%Y-%m-%d")
            )
            end_date = end_date + datetime.timedelta(days=1)
            queryset = queryset.filter(date_publish__lt=end_date)
        except ValueError:
            # datetimeに変換できない値はスルー
            pass

    # フィルタ:検索キーワード
    if "keyword" in querydict:
        keywords = querydict["keyword"].split()  # 全角/半角スペースで区切る
        for keyword in keywords:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(body__icontains=keyword)
            )

    # フィルタ: 並び順
    # デフォルトの並び順は投稿日の降順→created_atの降順
    if "sort" in querydict:
        sort_value = querydict["sort"]
        if sort_value == "date_publish_desc":
            pass  # 何もしない
        if sort_value == "date_publish_asc":
            queryset = queryset.order_by("date_publish", "created_at")

    # 公開中の投稿のみを表示する
    queryset = queryset.filter(is_published__exact=True)

    # ページネーション
    paginate_by = 10
    if "paginate_by" in querydict:
        try:
            paginate_by = int(querydict["paginate_by"])
        except ValueError:
            pass

    paginator = Paginator(queryset, paginate_by)
    page_number = 1
    if "page" in querydict:
        try:
            page_number = int(querydict["page"])
        except ValueError:
            # intに変換できない値はスルー
            pass
    page = paginator.get_page(page_number)
    context["post_list_page"] = page

    # ページネーションのナビゲーションに表示する番号を予め決めておく
    pagination_nav_numbers = []
    pagination_nav_display_first = False
    pagination_nav_display_last = False

    # 現在のページを中心として前後最大5ページ分を表示する
    # 上記の内、最初・最後のページを優先して表示する
    if paginator.num_pages >= 5:
        # 最初に、現在のページを真ん中にする
        left = page.number - 2
        right = page.number + 2
        # 左側か右側がページ範囲を逸脱する場合、その分を他方の側に加える
        if left < 1:
            right = right + (1 - left)
            left = 1
        elif right > paginator.num_pages:
            left = left - (right - paginator.num_pages)
            right = paginator.num_pages
        pagination_nav_numbers = list(range(left, right + 1))
        # 左端が2以上の場合、左端の代わりに最初のページを表示する
        if left > 1:
            pagination_nav_numbers.remove(left)
            pagination_nav_display_first = True
        # 右端が最後のページの1個前以下の場合、代わりに最後のページを表示する
        if right < paginator.num_pages:
            pagination_nav_numbers.remove(right)
            pagination_nav_display_last = True
    else:
        pagination_nav_numbers = list(range(1, paginator.num_pages + 1))

    context["post_list_pagination_nav"] = {
        "numbers": pagination_nav_numbers,
        "display_first": pagination_nav_display_first,
        "display_last": pagination_nav_display_last,
    }

    return render(request, "articleapp/search.html", context)


def search_tags(request):
    keyword = request.GET.get("keyword")
    tags = Tag.objects.all()
    if keyword is not None:
        tags = tags.filter(name__icontains=keyword)
    data = {"tags": list(tags.values())}
    return JsonResponse(data)


def post_detail(request, username, slug):
    user = get_object_or_404(
        User, username=username, is_staff=False, is_superuser=False
    )
    post = get_object_or_404(Post, user=user, slug=slug, is_published=True)
    other_posts = (
        Post.objects.filter(user=user, is_published=True)
        .exclude(id=post.id)[0:5]
    )
    context = {"post": post, "post_user": user, "other_posts": other_posts}
    return render(request, "articleapp/post_detail.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "articleapp/signup.html", {"form": form}, status=400)
    else:
        form = UserCreationForm()
        return render(request, "articleapp/signup.html", {"form": form})


def user_home(request, username, drafts=False):
    querydict = request.GET
    context = {}

    # urlで指定されたユーザー取得
    user_to_display = get_object_or_404(User, username=username, is_active=True)
    context["user_to_display"] = user_to_display

    # ログイン中のユーザーのページであるかどうかをコンテキストに保持する
    context["is_logged_in_user_home"] = False
    if request.user.is_authenticated and request.user == user_to_display:
        context["is_logged_in_user_home"] = True

    # ユーザーの公開中の投稿取得
    posts = Post.objects.filter(user=user_to_display, is_published=True)

    # 下書き一覧がリクエストされ、かつログイン中のユーザーであれば、下書きを取得する
    if drafts:
        if request.user.is_authenticated and request.user == user_to_display:
            posts = Post.objects.filter(user=user_to_display, is_published=False)
            # コンテキストで下書き一覧であることのフラグを保持
            context["drafts"] = True
        else:
            # ログイン中のユーザーでなければ通常のユーザーページにリダイレクトする
            return redirect("user_home", username=username)

    # ページネーション
    # ページネーター作成
    paginate_by = 10
    if "paginate_by" in querydict:
        try:
            paginate_by = int(querydict["paginate_by"])
        except ValueError:
            pass
    paginator = Paginator(posts, paginate_by)
    # ページ作成
    page_number = 1
    if "page" in querydict:
        try:
            page_number = int(querydict["page"])
        except ValueError:
            # intに変換できない値はスルー
            pass
    page = paginator.get_page(page_number)
    context["post_list_page"] = page
    context["post_list_pagination_nav"] = create_navigation_context_from_page(page)

    return render(request, "articleapp/user_home.html", context)


@login_required
def user_settings(request, current_menu_item="profile"):
    context = {"current_menu_item": current_menu_item}
    context["menu_items"] = [
        {"name": "profile", "label": "プロフィール", "url_name": "user_settings_profile"},
        {"name": "account", "label": "アカウント情報", "url_name": "user_settings_account"},
    ]

    form = ProfileUpdateForm(instance=request.user)
    if current_menu_item == "account":
        form = AccountUpdateForm(instance=request.user)

    if request.method == "POST":
        if current_menu_item == "profile":
            form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        elif current_menu_item == "account":
            form = AccountUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect(request.resolver_match.url_name)
        else:
            context["form"] = form
            return render(request, "articleapp/user_settings.html", context, status=400)

    context["form"] = form
    return render(request, "articleapp/user_settings.html", context)


@login_required
def deactivate(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.deactivate()

        return redirect("index")
    return render(request, "articleapp/deactivate.html")


@login_required
def post_create(request):
    context = {}

    if request.method == "POST":
        querydict = request.POST.copy()
        # QueryDictにuserフィールドの値を加える
        querydict["user"] = request.user

        # tagsフィールドにタグのリストをセットする
        tags_text = querydict["tags_text"].split()
        # 最大文字数を越えるタグが含まれていたらタグの取得・生成を行わずにエラーとする
        tag_name_max_length = Tag._meta.get_field("name").max_length
        has_invalid_length_tag = False  # 最大数を越えるタグが含まれているかをフラグで保持する
        if any([len(tag_text) > tag_name_max_length for tag_text in tags_text]):
            has_invalid_length_tag = True
        else:
            tags = [
                Tag.objects.get_or_create(name=tag_text)[0].id for tag_text in tags_text
            ]
            querydict.setlist("tags", tags)

        # フォームにデータを紐づける
        form = PostForm(querydict)
        if has_invalid_length_tag:
            form.add_error(
                "tags_text", ValidationError("1つのタグの文字数は最大100文字までです。", code="invalid")
            )

        if form.is_valid():
            post = form.save()
            next_url_name = "user_home"
            if form.cleaned_data["save_option"] == "save_and_publish":
                post.publish()
                next_url_name = "user_home"
            elif form.cleaned_data["save_option"] == "save_as_draft":
                next_url_name = "user_home_drafts"
            return redirect(next_url_name, username=request.user.username)
        else:
            context["form"] = form
            return render(request, "articleapp/post_create.html", context, status=400)

    form = PostForm()
    context["form"] = form
    return render(request, "articleapp/post_create.html", context)
