from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from bookapi.views import (
    BookViewSet,
    UserViewSet,
    GenreViewSet,
    ReviewViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"books", BookViewSet, "book")
router.register(r"genres", GenreViewSet, "genre")
router.register(r"reviews", ReviewViewSet, "review")

urlpatterns = [
    path("", include(router.urls)),
    path("login", UserViewSet.as_view({"post": "user_login"}), name="login"),
    path(
        "register", UserViewSet.as_view({"post": "register_account"}), name="register"
    ),
]
