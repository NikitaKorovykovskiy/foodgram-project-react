from django.contrib import admin

from user.models import Subscribe, User


class UserADmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email")
    list_filter = ("first_name", "email")


class SubscribeADmin(admin.ModelAdmin):
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
