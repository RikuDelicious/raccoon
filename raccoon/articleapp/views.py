from django.http import JsonResponse
from django.shortcuts import render

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
    querydict = request.GET
    context = {}

    return render(request, "articleapp/search.html", context)


def search_tags(request):
    keyword = request.GET.get("keyword")
    tags = Tag.objects.all()
    if keyword is not None:
        tags = tags.filter(name__contains=keyword)
    data = {"tags": list(tags.values())}
    return JsonResponse(data)
