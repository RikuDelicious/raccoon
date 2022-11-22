import datetime

from django.core.paginator import Paginator
from django.db.models import Q
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
        tags = querydict.getlist("tags")
        for tag in tags:
            queryset = queryset.filter(tags__name=tag)

    # フィルタ: 期間_開始
    if "period_start_date" in querydict:
        try:
            start_date = timezone.make_aware(
                datetime.datetime.strptime(querydict["period_start_date"], "%Y/%m/%d")
            )
            queryset = queryset.filter(date_publish__gte=start_date)
        except ValueError:
            # datetimeに変換できない値はスルー
            pass

    # フィルタ:期間_終了
    if "period_end_date" in querydict:
        try:
            end_date = timezone.make_aware(
                datetime.datetime.strptime(querydict["period_end_date"], "%Y/%m/%d")
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
        page_number = int(querydict["page"])
    page = paginator.get_page(page_number)
    context["post_list_page"] = page

    return render(request, "articleapp/search.html", context)


def search_tags(request):
    keyword = request.GET.get("keyword")
    tags = Tag.objects.all()
    if keyword is not None:
        tags = tags.filter(name__contains=keyword)
    data = {"tags": list(tags.values())}
    return JsonResponse(data)
