import datetime

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Post, Tag


# Create your views here.
def index(request):
    # tagをランダムに10個取得
    # order_by("?")でランダムに並べ替え
    tags = (
        Tag.objects.filter(post__isnull=False)  # 少なくとも1つ以上の投稿があるタグのみにする
        .filter(post__is_published=True)  # 少なくとも1つ以上の投稿が公開されているタグのみにする
        .order_by("?")[0:10]
    )

    # Postの新着5件を取得
    posts = Post.objects.filter(is_published=True).order_by("-date_publish")[0:5]

    return render(request, "articleapp/index.html", {"posts": posts, "tags": tags})


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
        ).filter(
            post_count__exact=len(tags)
        )
        
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

    # ページネーション
    paginator = Paginator(queryset, 10)
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
