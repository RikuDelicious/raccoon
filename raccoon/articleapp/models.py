import random
import string

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def generate_random_slug():
    seed = string.ascii_lowercase + string.digits
    random_chars = random.choices(seed, k=16)
    return "".join(random_chars)


# Create your models here.
class User(AbstractUser):
    display_name = models.CharField(max_length=100, null=True)
    profile_image = models.ImageField(upload_to="uploads/", null=True)

    username_validator = ASCIIUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    slug = models.SlugField(default=generate_random_slug)
    tags = models.ManyToManyField(to="Tag", blank=True)
    is_published = models.BooleanField(default=False)
    date_publish = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_publish", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "slug"], name="unique_user_slug"),
        ]

    def __str__(self):
        return self.title

    def publish(self):
        """
        投稿のステータスを公開中に切り替えて投稿日を記録する
        """
        if self.is_published:
            return
        self.is_published = True
        self.date_publish = timezone.now().date()
        self.save()

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"username": self.user, "slug": self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
