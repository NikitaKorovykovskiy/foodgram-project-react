from api.paginators import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from user.models import Subscribe, User
from user.serializers import SubscribeShowSerializer


class SubscribeUserViewSet(UserViewSet):
    """Кастомный вьюсет пользователя."""

    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    @action(
        detail=False,
        permission_classes=(IsAdminOrReadOnly,),
    )
    def subscriptions(self, request):
        follows = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(follows)
        serializer = SubscribeShowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(IsAdminOrReadOnly,),
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get("id"))
        serializer = SubscribeShowSerializer(
            author, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        data = {"author": author}
        serializer.create(data)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get("id"))
        if not Subscribe.objects.filter(
            user=request.user, author=author
        ).exists():
            return Response(
                {"errors": "Данная подписка не существует"},
                status=HTTP_400_BAD_REQUEST,
            )
        Subscribe.objects.filter(user=request.user, author=author).delete()
        return Response(status=HTTP_204_NO_CONTENT)
