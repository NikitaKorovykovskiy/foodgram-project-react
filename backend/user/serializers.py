from api.serializers import ShortRecipeSerializer
from django.conf import settings
from rest_framework import serializers
from user.models import Subscribe, User


class UserShowSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода пользователя/списка пользователей."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, username):
        user = self.context["request"].user
        return (
            not user.is_anonymous
            and Subscribe.objects.filter(
                user=user, following=username
            ).exists()
        )


class UserSerializer(serializers.ModelSerializer):
    """Основной кастомный сериализатор пользователя с доп. полями."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        min_length=4,
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "role",
        )

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError(
                "Пользователь с такой почтой уже зарегистрирован."
            )

        return data

    def validate_username(self, data):
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует."
            )

        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data["password"])
            user.save()
        except KeyError:
            pass
        return user


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    BANNED_NAMES = ("me", "admin", "ADMIN", "administrator", "moderator")

    class Meta:
        model = User
        fields = (
            "email",
            "username",
        )

    def validate_username(self, data):
        if data in self.BANNED_NAMES:
            raise serializers.ValidationError(
                "Нельзя использовать такое имя."
            )

        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует."
            )

        return data

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError(
                "Пользователь с такой почтой уже зарегистрирован."
            )

        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=24)


class SubscribeShowSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода пользователя/списка пользователей."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
        )
        read_only_fields = ("email", "username", "first_name", "last_name")

    def get_recipes(self, obj):
        """Получаем рецепты пользователя."""
        limit = (
            self.context.get("request").query_params.get("recipes_limit")
            or settings.LIMITRECIPE
        )
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = ShortRecipeSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user, following=obj
        ).exists()
