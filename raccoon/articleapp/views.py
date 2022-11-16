from django.shortcuts import render
from .models import Post, Tag


# Create your views here.
def index(request):
    # tagをランダムに10個取得
    # order_by("?")でランダムに並べ替え
    tags = Tag.objects.order_by("?")[0:10]

    # Postの新着5件を取得
    posts = Post.objects.filter(is_published=True).order_by("-date_publish")[0:5]

    return render(request, "articleapp/index.html", {"posts": posts, "tags": tags})
