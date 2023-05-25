from django.contrib import admin

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientMount,
    Recipe,
    Tag,
)


class IngredientInLine(admin.TabularInline):
    model = IngredientMount


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("author", "name", "cooking_time")
    search_fields = ("name", "author__username", "author__email")
    list_filter = ("tags",)
    inlines = [IngredientInLine]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = (
        "recipe__name",
        "recipe__author__username",
        "recipe__author__email",
    )
    list_filter = ("recipe__tags",)


@admin.register(Cart)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = (
        "recipe__name",
        "recipe__author__username",
        "recipe__author__email",
    )
    list_filter = ("recipe__tags",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "color")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)
