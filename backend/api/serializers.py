from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientMount,
    Recipe,
    Tag,
    TagRecipe,
)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from user.models import User


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
        model = IngredientMount
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
        model = IngredientMount
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
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientAmountGetSerializer(
        read_only=True, many=True, source="recipe_ingredients"
    )
    image = Base64ImageField()
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

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()


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
        lookup_field = "author"

    def add_ingredients(self, instance, ingredients):
        for ingredient in ingredients:
            ing, _ = IngredientMount.objects.get_or_create(
                ingredient_id=ingredient["id"], amount=ingredient["amount"]
            )
            instance.ingredients.add(ing)
        return instance

    @transaction.atomic
    def create(self, validated_data):
        tags_set = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        TagRecipe.objects.bulk_create(
            TagRecipe(recipe=recipe, tag=tag) for tag in tags_set
        )
        IngredientMount.objects.bulk_create(
            IngredientMount(
                ingredient=ingredient["id"],
                recipe=recipe,
                amount=ingredient["amount"],
            )
            for ingredient in ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get("tags")
        instance.tags.set(tags_data)
        IngredientMount.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get("ingredients")
        for ingredient in ingredients:
            IngredientMount.objects.create(
                ingredient=ingredient["id"],
                recipe=instance,
                amount=ingredient["amount"],
            )
        instance.save()
        return instance

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
                            "ингредиента больше 0"
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

    def validate(self, data):
        user = self.context.get("request").user
        recipe = self.context.get("recipe_id")
        if Favorite.objects.filter(
            user=user, favorite_recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                {"errors": "Рецепт уже в избранном"}
            )
        return data


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

    def validate(self, data):
        user = self.context.get("request").user
        recipe = self.context.get("recipe_id")
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {"errors": "Рецепт уже добавлен в список покупок"}
            )
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
