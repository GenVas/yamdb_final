from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    ConfirmationViewSet,
    GenreViewSet,
    RegistrationView,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
)

v1_router = DefaultRouter()

v1_router.register(r"users", UserViewSet, basename="users")
v1_router.register(r"categories", CategoryViewSet, basename="categories")
v1_router.register(r"genres", GenreViewSet, basename="genres")
v1_router.register(r"titles", TitleViewSet, basename="titles")
v1_router.register(
    r"^titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="reviews",
)
v1_router.register(
    r"^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

authpatterns = [
    path("token/", ConfirmationViewSet.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", RegistrationView.as_view(), name="auth_register"),
]

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/auth/", include(authpatterns)),
]
