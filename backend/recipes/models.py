from django.core.validators import MinValueValidator
from django.db import models
from ingredients.models import Ingredient
from tags.models import Tag
from user.models import User


class Recipe(models.Model):
    """Модель описывающая доступные поля для рецепта"""

    created = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
        help_text="Автоматически устанавливается текущая дата и время",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        help_text="Выберите из списка автора",
    )
    name = models.CharField(
        "Название", max_length=120, help_text="Введите название"
    )
    image = models.ImageField(
        "Картинка",
        upload_to="recipes/",
        help_text="Выберите картинку",
    )
    text = models.TextField(
        "Текстовое описание", help_text="Введите текстовое описание"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления в минутах",
        help_text="Введите время приготовления в минутах",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        verbose_name="Ингредиенты",
        help_text="Выберите ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        through="TagRecipe",
        verbose_name="Теги",
        help_text="Выберите теги",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class RecipeRelated(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт",
    )

    class Meta:
        abstract = True


class TagRecipe(RecipeRelated):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name="Тег",
        help_text="Выберите из списка тег",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_recipe_tag",
                fields=["recipe", "tag"],
            ),
        ]
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецептов"


class IngredientInRecipe(RecipeRelated):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент рецепта",
        help_text="Выберите ингредиент рецепта",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество ингридиента",
        help_text="Введите количество ингридиента",
        validators=[
            MinValueValidator(
                1, message="Укажите количество больше либо равное 1"
            ),
        ],
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецептов"

    def __str__(self) -> str:
        return f"{self.ingredient} {self.recipe} {self.amount}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
        help_text="Выберите рецепт",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Списки Избранное"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="unique_user_favorite_recipe",
            ),
        )

    def __str__(self):
        return f"{self.user} -> {self.recipe}"


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
        help_text="Выберите рецепты для добавления в корзины",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="unique_user_cart_recipe",
            ),
        )

    def __str__(self):
        return f"{self.user} -> {self.recipe}"
