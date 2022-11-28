from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("search_tags/", views.search_tags, name="search_tags"),
    path("<str:username>/posts/<slug:slug>/", views.post_detail, name="post_detail"),
    # User認証関連
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        LoginView.as_view(
            template_name="articleapp/login.html",
            next_page=reverse_lazy("index"),
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
