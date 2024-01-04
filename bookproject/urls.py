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
router.register(r"alien_users", UserViewSet, "alien_user")


urlpatterns = [
    path("", include(router.urls)),
    path("login", UserViewSet.as_view({"post": "user_login"}), name="login"),
    path(
        "register", UserViewSet.as_view({"post": "register_account"}), name="register"
    ),
    path(
        "alien_users/currentUser/update",
        UserViewSet.as_view({"put": "update_alien_user_profile"}),
        name="update_alien_user",
    ),
]
