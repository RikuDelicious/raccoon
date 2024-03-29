# Generated by Django 4.1.3 on 2022-12-05 15:33

import articleapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articleapp", "0008_alter_user_display_name_alter_user_profile_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="body",
            field=models.TextField(verbose_name="本文"),
        ),
        migrations.AlterField(
            model_name="post",
            name="slug",
            field=models.SlugField(
                default=articleapp.models.generate_random_slug, verbose_name="スラッグ"
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="tags",
            field=models.ManyToManyField(
                blank=True, to="articleapp.tag", verbose_name="タグ"
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=200, verbose_name="タイトル"),
        ),
        migrations.AlterField(
            model_name="user",
            name="display_name",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="ニックネーム"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="profile_image",
            field=models.ImageField(
                blank=True, null=True, upload_to="uploads/", verbose_name="プロフィール画像"
            ),
        ),
    ]
