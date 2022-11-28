import datetime
import random

from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import UserCreationForm
from .models import Post, Tag, User


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
    posts = Post.objects.filter(is_published=True).order_by("-date_publish")[0:5]

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
    # デフォルトは投稿日の降順
    queryset = queryset.order_by("-date_publish")
    if "sort" in querydict:
        sort_value = querydict["sort"]
        if sort_value == "date_publish_desc":
            pass  # 何もしない
        if sort_value == "date_publish_asc":
            queryset = queryset.order_by("date_publish")

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
        .exclude(id=post.id)
        .order_by("-date_publish")[0:5]
    )
    context = {"post": post, "post_user": user, "other_posts": other_posts}
    return render(request, "articleapp/post_detail.html", context)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.GET)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "articleapp/signup.html", {"form": form})
    else:
        form = UserCreationForm()
        return render(request, "articleapp/signup.html", {"form": form})
