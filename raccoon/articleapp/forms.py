from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import ModelForm

from .models import User
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
