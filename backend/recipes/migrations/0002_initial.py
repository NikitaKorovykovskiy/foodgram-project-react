# Generated by Django 4.2.1 on 2023-05-22 12:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tags", "0001_initial"),
        ("ingredients", "0001_initial"),
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                help_text="Выберите из списка автора",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                help_text="Выберите ингредиенты",
                through="recipes.IngredientInRecipe",
                to="ingredients.ingredient",
                verbose_name="Ингредиенты",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                help_text="Выберите теги",
                through="recipes.TagRecipe",
                to="tags.tag",
                verbose_name="Теги",
            ),
        ),
        migrations.AddField(
            model_name="ingredientinrecipe",
            name="ingredient",
            field=models.ForeignKey(
                help_text="Выберите ингредиент рецепта",
                on_delete=django.db.models.deletion.CASCADE,
                to="ingredients.ingredient",
                verbose_name="Ингредиент рецепта",
            ),
        ),
        migrations.AddField(
            model_name="ingredientinrecipe",
            name="recipe",
            field=models.ForeignKey(
                help_text="Выберите рецепт",
                on_delete=django.db.models.deletion.CASCADE,
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="recipe",
            field=models.ForeignKey(
                help_text="Выберите рецепт",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                help_text="Выберите пользователя",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddField(
            model_name="cart",
            name="recipe",
            field=models.ForeignKey(
                help_text="Выберите рецепты для добавления в корзины",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_cart",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddField(
            model_name="cart",
            name="user",
            field=models.ForeignKey(
                help_text="Выберите пользователя",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_cart",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddConstraint(
            model_name="tagrecipe",
            constraint=models.UniqueConstraint(
                fields=("recipe", "tag"), name="unique_recipe_tag"
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_favorite_recipe"
            ),
        ),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_cart_recipe"
            ),
        ),
    ]
