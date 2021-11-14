from smtplib import SMTPException

from django.core.mail import EmailMessage
from django.db.models import Avg, ExpressionWrapper, Func, Q, fields
from django.http import JsonResponse
from django.http import response as response_http
from rest_framework import (filters, generics, mixins, pagination, permissions,
                            response, status, views, viewsets)
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User
from reviews.tokens import account_activation_token

from api.filters import TitleFilter
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             OwnerAdminModeratorOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             ConfirmationTokenSerializer, GenreSerializer,
                             ReadTitleSerializer, RegistrationSerializer,
                             ReviewSerializer, UserSerializer,
                             WriteTitleSerializer)


class ConfirmationViewSet(views.APIView):
    """Provides access and refresh tokens in response to code
    confirmation and email and activate a user
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ConfirmationTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data.get("confirmation_code")
        username = serializer.validated_data.get("username")
        user = generics.get_object_or_404(User, username=username)
        if account_activation_token.check_token(user, confirmation_code):
            refresh_token = RefreshToken.for_user(user)
            return JsonResponse(
                {
                    "access_token": str(refresh_token.access_token),
                    "refresh_token": str(refresh_token),
                }
            )
        return response_http.Response(
            "Invalid token.",
            status=status.HTTP_400_BAD_REQUEST,
        )


class RegistrationView(generics.CreateAPIView):
    """ "Create a new user and send a confirmation code
    message to the user's email using the 'send_mail' function
    """

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer

    def send_mail(self, user):
        """Send confirmation_code to user"""
        confirmation_code = account_activation_token.make_token(user)
        try:
            message = (
                f"{user.username} Пожалуйста, подтвердите свой адрес"
                " электронной почты, чтобы"
                "завершите регистрацию, используя"
                f" токен: {confirmation_code}"
            )
            to_email = user.email
            mail_subject = "Активируйте вашу учетную запись."
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
        except Exception as e:
            raise SMTPException(
                f"Что-то пошло не так. Не могу отправить письмо: {e}",
            )

    def create(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")
        users = User.objects.filter(Q(email=email) | Q(username=username))
        if not users.exists():
            user = User.objects.create(email=email, username=username)
        else:
            user = users.first()
            if user.email != email or user.username != username:
                return response.Response(
                    serializer.data, status=status.HTTP_400_BAD_REQUEST
                )
        self.send_mail(user)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Provides work with user and his profile depending
    on permission and role
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    pagination_class = pagination.LimitOffsetPagination

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def get_self_user_page(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class Round(Func):
    """Round query output to integer."""

    function = "ROUND"
    template = "%(function)s(%(expressions)s)"


class CustomizedListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Base ViewSet for Categories & Genres.
    Allowed actions: `list`, `create`, `destroy`.
    Other actions returns HTTP 405.
    """

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ("name",)
    search_fields = ("name",)
    lookup_field = "slug"
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(CustomizedListCreateDestroyViewSet):
    """Viewset for Categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CustomizedListCreateDestroyViewSet):
    """Viewset for Genres."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset for Titles."""

    queryset = Title.objects.prefetch_related("reviews").annotate(
        rating=ExpressionWrapper(
            Round(Avg("reviews__score")),
            output_field=fields.IntegerField(),
        )
    )
    ordering_fields = ("name",)
    filterset_class = TitleFilter
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        """Manage serializer.
        `list`&`retreive` - ReadTitleSerializer.
        For other actions - WriteTitleSerializer.
        """
        if self.action == "retrieve" or self.action == "list":
            return ReadTitleSerializer
        return WriteTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset for reviews."""

    serializer_class = ReviewSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (
        OwnerAdminModeratorOrReadOnly,
    )

    def get_queryset(self):
        """Return queryset for ViewSet.
        Get particular title with `title_id`.
        Get all reviews for patricular title.
        """
        title = generics.get_object_or_404(
            Title,
            id=self.kwargs.get("title_id"),
        )
        return title.reviews.select_related("author").all()

    def perform_create(self, serializer):
        """Creating review.
        Get particular title with `title_id`.
        Explicitly point review`s title.
        Explicitly point review`s author.
        """
        title_id = self.kwargs.get("title_id")
        title = generics.get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset for comments."""

    serializer_class = CommentSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (
        OwnerAdminModeratorOrReadOnly,
    )

    def get_queryset(self):
        """Return queryset for ViewSet.
        Get particular review with `review_id`.
        Get all comments for patricular review.
        """
        review = generics.get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
        )
        return review.comments.select_related("author").all()

    def perform_create(self, serializer):
        """Creating comment.
        Explicitly point comment`s author.
        Explicitly point comment`s review.
        """
        review_id = self.kwargs.get("review_id")
        review = generics.get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
