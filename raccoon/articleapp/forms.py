from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import ModelForm

from .models import Post, User
from .widgets import ClearableFileInput


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["display_name", "profile_image"]
        widgets = {
            "profile_image": ClearableFileInput(),
        }


class AccountUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["username"]


POST_SAVE_OPTION_CHOICES = [
    ("save_and_publish", "投稿する"),
    ("save_as_draft", "下書き保存する"),
]


class PostForm(ModelForm):
    tags_text = forms.CharField(max_length=200, required=False, label="タグ")
    save_option = forms.ChoiceField(
        choices=POST_SAVE_OPTION_CHOICES, initial=POST_SAVE_OPTION_CHOICES[0][0]
    )

    class Meta:
        model = Post
        fields = ["title", "slug", "tags", "body", "user"]
