from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers
from rest_framework.validators import (
    UniqueTogetherValidator,
    UniqueValidator,
)

from ingredients.models import Ingredient
from recipes.models import (
    Cart,
    Favorite,
    IngredientInRecipe,
    Recipe,
    # TagRecipe,
)
from tags.models import Tag
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
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientAmountGetSerializer(
        read_only=True, many=True, source="recipe_ingredients"
    )
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

    def validate_tags(self, value):
        if not value:
            raise exceptions.ValidationError(
                "Нужно добавить хотя бы один тег."
            )

        return value

    def validate_ingredients(self, value):
        if not value:
            raise exceptions.ValidationError(
                "Нужно добавить хотя бы один ингредиент."
            )

        ingredients = [item["id"] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    "У рецепта не может быть два одинаковых ингредиента."
                )

        return value

    def create(self, validated_data):
        author = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient["amount"]
            ingredient = get_object_or_404(Ingredient, pk=ingredient["id"])

            Ingredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient["amount"]
                ingredient = get_object_or_404(
                    Ingredient, pk=ingredient["id"]
                )

                Ingredient.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={"amount": amount},
                )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(
            instance, context={"request": self.context.get("request")}
        )

        return serializer.data

    class Meta:
        model = Recipe
        exclude = ("pub_date",)

    # class Meta:
    #     model = Recipe
    #     fields = (
    #         "ingredients",
    #         "tags",
    #         "image",
    #         "author",
    #         "name",
    #         "text",
    #         "cooking_time",
    #     )
    #     # lookup_field = "author"

    # def add_ingredients(self, ingredients_data, recipe):
    #     for ingredient in ingredients_data:
    #         IngredientInRecipe.objects.create(
    #             recipe=recipe,
    #             amount=ingredient["amount"],
    #             ingredient=ingredient["id"],
    #         )

    # def add_tags(self, tags, recipe):
    #     for tag in tags:
    #         recipe.tags.add(tag)

    # def create(self, validated_data):
    #     image_data = validated_data.pop("image")
    #     ingredients_data = validated_data.pop("ingredients")
    #     tag_data = validated_data.pop("tags")
    #     recipe = Recipe.objects.create(image=image_data, **validated_data)
    #     self.add_tags(tag_data, recipe)
    #     self.add_ingredients(ingredients_data, recipe)
    #     return recipe

    # def to_representation(self, instance):
    #     request = self.context.get("request")
    #     context = {"request": request}
    #     return RecipeGetSerializer(instance, context=context).data

    # def update(self, instance, validated_data):
    #     tags = validated_data.pop("tags", None)
    #     if tags is not None:
    #         instance.tags.set(tags)

    #     ingredients = validated_data.pop("ingredients", None)
    #     if ingredients is not None:
    #         instance.ingredients.clear()

    #         for ingredient in ingredients:
    #             amount = ingredient["amount"]
    #             ingredient = get_object_or_404(
    #                 Ingredient, pk=ingredient["id"]
    #             )

    #             Recipe.objects.update_or_create(
    #                 recipe=instance,
    #                 ingredient=ingredient,
    #                 defaults={"amount": amount},
    #             )

    #     return super().update(instance, validated_data)

    # def validate(self, data):
    #     ingredients = self.initial_data.get("ingredients")
    #     if not ingredients:
    #         raise serializers.ValidationError(
    #             {"ingredients": "Нужен хоть один ингридиент для рецепта"}
    #         )
    #     ids = [item["id"] for item in ingredients]
    #     if len(ids) != len(set(ids)):
    #         raise serializers.ValidationError(
    #             "Ингредиенты в рецепте должны быть уникальными!"
    #         )
    #     for ingredient_item in ingredients:
    #         if int(ingredient_item["amount"]) < 1:
    #             raise serializers.ValidationError(
    #                 {
    #                     "ingredients": (
    #                         "Убедитесь, что значение количества "
    #                         "ингредиента больше 1"
    #                     )
    #                 }
    #             )
    #     return data


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
