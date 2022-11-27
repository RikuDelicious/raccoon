from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("search_tags/", views.search_tags, name="search_tags"),
    path("<str:username>/posts/<slug:slug>/", views.post_detail, name="post_detail"),
]
