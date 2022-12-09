from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("search_tags/", views.search_tags, name="search_tags"),
    path("new/", views.post_create, name="post_create"),
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
        "settings/",
        RedirectView.as_view(pattern_name="user_settings_profile"),
        name="user_settings",
    ),
    path(
        "settings/profile/",
        views.user_settings,
        name="user_settings_profile",
        kwargs={"current_menu_item": "profile"},
    ),
    path(
        "settings/account/",
        views.user_settings,
        name="user_settings_account",
        kwargs={"current_menu_item": "account"},
    ),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="articleapp/password_change.html",
            success_url=reverse_lazy("user_settings_account"),
        ),
        name="password_change",
    ),
    path("deactivate/", views.deactivate, name="deactivate"),
    # ユーザー関連ページ（先頭が任意のユーザー名のため末尾にまとめる）
    path("<str:username>/home/", views.user_home, name="user_home"),
    path(
        "<str:username>/home/drafts/",
        views.user_home,
        name="user_home_drafts",
        kwargs={"drafts": True},
    ),
    path("<str:username>/posts/<slug:slug>/", views.post_detail, name="post_detail"),
    path(
        "<str:username>/posts/<slug:slug>/update/",
        views.post_update,
        name="post_update",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
