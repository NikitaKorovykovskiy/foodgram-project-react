from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient
from recipes.models import IngredientInRecipe  # TagRecipe,
from recipes.models import Cart, Favorite, Recipe
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import (
    UniqueTogetherValidator,
    UniqueValidator,
)
from tags.models import Tag
from user.models import User


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=200,
        validators=(UniqueValidator(queryset=Tag.objects.all()),),
    )

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        lookup_field = "slug"


class BaseIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientAmountGetSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class IngredientAmountPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class UserDetailSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name="is_subscribed"
    )

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

    def is_subscribed(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and obj.subscribing.filter(user=user).exists()
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("ingredientinrecipe__amount"),
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()

    # def get_is_favorited(self, obj):
    #     request = self.context.get("request")
    #     if request is None or request.user.is_anonymous:
    #         return False
    #     return Favorite.objects.filter(
    #         user=request.user, recipe__id=obj.id
    #     ).exists()

    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get("request")
    #     if request is None or request.user.is_anonymous:
    #         return False
    #     return Cart.objects.filter(
    #         user=request.user, recipe__id=obj.id
    #     ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientAmountPostSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "author",
            "name",
            "text",
            "cooking_time",
        )
        # lookup_field = "author"

    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient=Ingredient.objects.get(id=ingredient["id"]),
                    recipe=recipe,
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(
            recipe=recipe, ingredients=ingredients
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance, ingredients=ingredients
        )
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeGetSerializer(instance, context=context).data

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужен хоть один ингридиент для рецепта"}
            )
        ids = [item["id"] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты в рецепте должны быть уникальными!"
            )
        for ingredient_item in ingredients:
            if int(ingredient_item["amount"]) < 1:
                raise serializers.ValidationError(
                    {
                        "ingredients": (
                            "Убедитесь, что значение количества "
                            "ингредиента больше 1"
                        )
                    }
                )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(
        max_length=None,
        use_url=False,
    )

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time")
        validators = UniqueTogetherValidator(
            queryset=Favorite.objects.all(), fields=("user", "recipe")
        )


class CartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(
        max_length=None,
        use_url=False,
    )

    class Meta:
        model = Cart
        fields = ("id", "name", "image", "cooking_time")
        validators = UniqueTogetherValidator(
            queryset=Cart.objects.all(), fields=("user", "recipe")
        )
