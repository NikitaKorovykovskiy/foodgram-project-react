# Generated by Django 4.2 on 2023-05-09 03:30

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ingredient",
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
                    "name",
                    models.CharField(
                        help_text="Введите название",
                        max_length=150,
                        verbose_name="Название",
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(
                        help_text="Введите единицу измерения",
                        max_length=150,
                        verbose_name="Единица измерения",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
                "ordering": ("name", "measurement_unit"),
            },
        ),
        migrations.AddConstraint(
            model_name="ingredient",
            constraint=models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_ingridient"
            ),
        ),
    ]