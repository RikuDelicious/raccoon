from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random, string

def generate_random_slug():
    seed = string.ascii_lowercase + string.digits
    random_chars = random.choices(seed, k=16)
    return ''.join(random_chars)

# Create your models here.
class User(AbstractUser):
    display_name = models.CharField(max_length=100, null=True)


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    slug = models.SlugField(default=generate_random_slug)
    tags = models.ManyToManyField(to="Tag", blank=True)
    is_published = models.BooleanField(default=False)
    date_publish = models.DateField(null=True)
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


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
