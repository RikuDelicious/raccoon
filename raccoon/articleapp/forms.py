from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import ModelForm

from .models import User


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "display_name", "profile_image"]
