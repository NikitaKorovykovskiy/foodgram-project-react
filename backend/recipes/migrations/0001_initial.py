# Generated by Django 4.2.1 on 2023-05-22 12:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tags", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Список покупок",
                "verbose_name_plural": "Списки покупок",
            },
        ),
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Избранное",
                "verbose_name_plural": "Списки Избранное",
            },
        ),
        migrations.CreateModel(
            name="IngredientInRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        help_text="Введите количество ингридиента",
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, message="Укажите количество больше либо равное 1"
                            )
                        ],
                        verbose_name="Количество ингридиента",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент рецепта",
                "verbose_name_plural": "Ингредиенты рецептов",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Автоматически устанавливается текущая дата и время",
                        verbose_name="Дата создания",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Введите название",
                        max_length=120,
                        verbose_name="Название",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="Выберите картинку",
                        upload_to="recipes/",
                        verbose_name="Картинка",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Введите текстовое описание",
                        verbose_name="Текстовое описание",
                    ),
                ),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        help_text="Введите время приготовления в минутах",
                        verbose_name="Время приготовления в минутах",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="TagRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        help_text="Выберите рецепт",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="recipes.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        help_text="Выберите из списка тег",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tags.tag",
                        verbose_name="Тег",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тег рецепта",
                "verbose_name_plural": "Теги рецептов",
            },
        ),
    ]
