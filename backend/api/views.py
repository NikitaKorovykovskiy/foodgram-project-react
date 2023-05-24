from http import HTTPStatus

from api.filter import AuthorAndTagFilter, IngredientSearchFilter
from api.paginators import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    BaseIngredientSerializer,
    CartSerializer,
    FavoriteSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    RecipeShortSerializer,
)
from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from ingredients.models import Ingredient
from recipes.models import Cart, Favorite, IngredientInRecipe, Recipe
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from tags.models import Tag
from tags.serializers import TagSerializer

CONTENT_TYPE = "text/plain"


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AuthorAndTagFilter
    # filterset_fields = ['created']
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = LimitPageNumberPagination

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.__add_to(Favorite, request.user, pk)
        return self.__delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.__add_to(Cart, request.user, pk)
        return self.__delete_from(Cart, request.user, pk)

    def __add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "Рецепт уже добавлен!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def __delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Рецепт уже удален!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        return ingredients_export(self, request, ingredients)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = BaseIngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = IngredientSearchFilter
    search_fields = ("^name",)


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    model = Favorite

    def create(self, request, *args, **kwargs):
        recipe_id = int(self.kwargs["recipes_id"])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteSerializer()
        return Response(
            serializer.to_representation(instance=recipe),
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs["recipes_id"]
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id
        )
        object.delete()
        return Response(HTTPStatus.NO_CONTENT)


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CartSerializer
    pagination_class = LimitPageNumberPagination
    queryset = Cart.objects.all()
    model = Cart

    def create(self, request, *args, **kwargs):
        recipe_id = int(self.kwargs["recipes_id"])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(user=request.user, recipe=recipe)
        serializer = CartSerializer()
        return Response(
            serializer.to_representation(instance=recipe),
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs["recipes_id"]
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id
        )
        object.delete()
        return Response(HTTPStatus.NO_CONTENT)

    def download(self, request):
        shopping_list = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .order_by("ingredient__name")
            .annotate(ingredient_total=Sum("amount"))
        )

        content = [
            f'{item["ingredient__name"]}'
            f'({item["ingredient__measurement_unit"]})'
            f'- {item["ingredient_total"]}\n'
            for item in shopping_list
        ]
        response = HttpResponse(content, content_type=CONTENT_TYPE)
        response[
            "Content-Disposition"
        ] = f"attachment; filename={settings.FILENAME}"
        return response
