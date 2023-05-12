from django.core import validators
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        "Название",
        unique=True,
        max_length=150,
        help_text="Введите название",
    )
    color = models.CharField(
        "Цвет",
        unique=True,
        max_length=7,
        help_text="Введите цвет в RGB-формате (#rrggbb)",
        validators=[
            validators.RegexValidator(
                r"^#[a-fA-F0-9]{6}$",
                "Используйте RGB-формат для указания цвета (#AABBCC)",
            )
        ],
    )
    slug = models.SlugField(
        "Slug",
        unique=True,
        max_length=150,
        help_text="Введите slug",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"
