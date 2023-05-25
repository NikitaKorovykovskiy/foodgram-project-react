from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from user.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        help_text="Введите название тега",
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name="Идентификатор",
        max_length=200,
        unique=True,
        help_text="Введите текстовый идентификатор тега",
    )
    color = ColorField(
        verbose_name="Цвет",
        default="#FF0000",
        max_length=7,
        help_text="Введите цвет в RGB-формате (#rrggbb)",
    )
    slug = models.SlugField(
        "Slug",
        unique=True,
        max_length=150,
        help_text="Введите slugs",
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
        help_text="Введите название продуктов",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единицы измерения",
        help_text="Введите единицы измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    created = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
        help_text="Автоматически устанавливается текущая дата и время",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
        help_text="Выберите автора рецепта",
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        help_text="Введите название рецепта",
        max_length=200,
    )
    image = models.ImageField(
        "Картинка",
        upload_to="recipes/",
        blank=True,
        help_text="Выберите изображение рецепта",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Введите описания рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientMount",
        related_name="ingredients",
        verbose_name="Ингредиент",
        help_text="Выберите ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        through="TagRecipe",
        related_name="tags",
        verbose_name="Тэг",
        help_text="Выберите тэги",
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(1),),
        verbose_name="Время приготовления",
        help_text="Введите время приготовления",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("created",)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name="Теги",
        help_text="Выберите теги рецепта",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт",
    )

    class Meta:
        verbose_name = "Теги рецепта"
        verbose_name_plural = "Теги рецепта"

    def __str__(self):
        return f"{self.tag} {self.recipe}"


class IngredientMount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Продукты рецепта",
        help_text="Добавьте продукты, необходимые по рецепту",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
        help_text="Выберите рецепт",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество ингредиента",
        help_text="Введите количество продукта",
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = "Продукты в рецепте"
        verbose_name_plural = "Продукты в рецепте"

    def __str__(self):
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
