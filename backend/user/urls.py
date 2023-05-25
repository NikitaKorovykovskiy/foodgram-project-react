from django.urls import include, path

from rest_framework.routers import DefaultRouter


from .views import SubscribeUserViewSet


app_name = "user"


router = DefaultRouter()

router.register("users", SubscribeUserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
