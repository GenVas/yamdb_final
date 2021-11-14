from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('text', 'title', 'score')


@admin.register(models.Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        "name", "year", "description", "category",
    )
    search_fields = ("name",)
    empty_value_display = '-empty-'


@admin.register(models.User)
class MyUserAdmin(UserAdmin):

    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_active",
        "bio",
    ]
    list_editable = ("role",)
    fieldsets = (
        (
            None,
            {"fields": ("username", "email", "password", "role", "bio")},
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "bio",
                    "role",
                ),
            },
        ),
    )
    ordering = ("email",)
    search_fields = ("username", "role")
    list_filter = (
        "role",
        "is_active",
    )
