from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("search_tags/", views.search_tags, name="search_tags"),
    # User認証関連
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        LoginView.as_view(
            template_name="articleapp/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "settings/profile/",
        views.user_settings,
        name="user_settings_profile",
        kwargs={"menu": "profile"},
    ),
    path(
        "settings/account/",
        views.user_settings,
        name="user_settings_account",
        kwargs={"menu": "account"},
    ),
    # ユーザー関連ページ（先頭が任意のユーザー名のため末尾にまとめる）
    path("<str:username>/home/", views.user_home, name="user_home"),
    path(
        "<str:username>/home/drafts/",
        views.user_home,
        name="user_home_drafts",
        kwargs={"drafts": True},
    ),
    path("<str:username>/posts/<slug:slug>/", views.post_detail, name="post_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
