from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UltraAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(UltraAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email")
    list_filter = ("first_name", "email")


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "following",
    )
    search_fields = (
        "following__email",
        "following__username",
    )
