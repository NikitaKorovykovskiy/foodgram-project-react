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
)
from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from ingredients.models import Ingredient
from recipes.models import Cart, Favorite, IngredientInRecipe, Recipe
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from tags.models import Tag
from tags.serializers import TagSerializer

CONTENT_TYPE = "text/plain"


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AuthorAndTagFilter
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     serializer = RecipeGetSerializer(instance=serializer.instance)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # partial = kwargs.get("partial", None)
        # instance = self.get_object()
        # serializer = self.get_serializer(
        #     instance, data=request.data, partial=partial
        # )
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        # serializer = RecipePostSerializer(instance=serializer.instance)
        # headers = self.get_success_headers(serializer.data)
        # return Response(
        #     serializer.data, status=status.HTTP_200_OK, headers=headers
        # )
        pk = kwargs.get("pk", None)
        instance = Recipe.objects.get(pk=pk)
        serializer = RecipePostSerializer(
            data=request.data, instance=instance
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
