from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя"""

    USER = "user"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (USER, "Пользователь"),
        (ADMIN, "Администратор"),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Уникальное имя",
        help_text="Введите уникальное имя пользователя",
    )
    password = models.CharField(max_length=150, verbose_name="пароль")
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя",
        help_text="Введите имя пользователя",
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Фамилия",
        help_text="Введите фамилию пользователя",
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Электронная почта",
        help_text="Введите электронную почту пользователя",
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name="Подписка на данного пользователя",
        help_text="Отметьте для подписки на данного пользователя",
    )
    role = models.CharField(
        "Пользовательская роль",
        max_length=15,
        choices=ROLE_CHOICES,
        default=USER,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.is_staff or self.role == self.ADMIN


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
        help_text="Выберите пользователя, который подписывается",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
        help_text="Выберите автора, на которого подписываются",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} {self.following}"
