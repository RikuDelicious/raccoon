from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


# Register your models here.
@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    def get_fieldsets(self, request, obj=None):
        # ユーザー追加フォームにはデフォルトのフィールドを表示する
        if obj is None:
            return self.add_fieldsets

        # 以下、ユーザー編集フォームのフィールド
        fields_top = (
            "username",
            "password",
        )

        # スタッフ・スーパーユーザー以外はdisplay_nameを表示する
        if not (obj.is_staff or obj.is_superuser):
            fields_top += ("display_name",)

        fieldsets = (
            (None, {"fields": fields_top}),
            (f"{_('Personal info')} (staff, superuser only)", {"fields": ("email",)}),
            (
                _("Permissions"),
                {
                    "fields": (
                        "is_active",
                        "is_staff",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    ),
                },
            ),
            (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        # スタッフ・スーパーユーザーのみemailフィールドを入力可能にする
        if obj is not None and (obj.is_staff or obj.is_superuser):
            return tuple()
        return ("email",)


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass
