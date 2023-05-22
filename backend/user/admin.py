from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import Subscribe, User


class UserADmin(UserAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email")
    list_filter = ("first_name", "email")


class SubscribeADmin(UserAdmin):
    list_display = (
        "user",
        "following",
    )
    search_fields = (
        "following__email",
        "following__username",
    )


admin.site.register(User, UserADmin)
admin.site.register(Subscribe, SubscribeADmin)
