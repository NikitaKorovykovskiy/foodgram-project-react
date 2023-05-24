from django.contrib import admin
from recipes.models import (Cart, Favorite, Ingredient, IngredientInRecipe,
                            Recipe)

EMPTY = "< Тут Пусто >"


class IngredientInLine(admin.TabularInline):
    model = IngredientInRecipe
    raw_id_fields = ["ingredient"]


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("author", "name", "cooking_time")
    search_fields = ("name", "author__username", "author__email")
    list_filter = ("tags",)
    inlines = [IngredientInLine]


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = (
        "recipe__name",
        "recipe__author__username",
        "recipe__author__email",
    )
    list_filter = ("recipe__tags",)


class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = (
        "recipe__name",
        "recipe__author__username",
        "recipe__author__email",
    )
    list_filter = ("recipe__tags",)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Cart, CartAdmin)
