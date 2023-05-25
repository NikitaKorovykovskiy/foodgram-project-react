from django.contrib import admin


from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )

    list_editable = (
        "name",
        "color",
        "slug",
    )

    search_fields = (
        "name",
        "slug",
    )

    list_filter = ("name",)
