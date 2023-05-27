from api.paginators import LimitPageNumberPagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from user.models import Subscribe, User
from user.serializers import SubscribeShowSerializer


class SubscribeUserViewSet(UserViewSet):
    """Кастомный вьюсет пользователя."""

    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="subscribe",
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        follow = Subscribe.objects.filter(
            user=request.user, following=author
        )
        if request.method == "POST":
            if author == request.user:
                error = {"errors": "Вы пытаетесь подписаться на себя."}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            author, created = Subscribe.objects.get_or_create(
                user=request.user, following=author
            )
            if not created:
                error = {
                    "errors": "Вы уже подписаны на этого пользователя."
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeShowSerializer(
                author, context={"request": request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        if not follow.exists():
            error = {
                "errors": "Вы не были подписаны на этого пользователя."
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def subscriptions(self, request):
        follows = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(follows)
        serializer = SubscribeShowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
