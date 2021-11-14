from django.core.exceptions import ValidationError
from rest_framework import serializers
from reviews.models import (
    Category, Comment, Genre,
    # GenreTitle,
    Review, Title, User
)


class ConfirmationTokenSerializer(serializers.Serializer):
    """Serializing verification data to provide full user registration"""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class RegistrationSerializer(serializers.Serializer):
    """Serializing data to provide a user creation"""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate(self, data):
        if data["username"] == "me":
            raise ValidationError("Пользователь не может иметь имя 'me'")
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializing data for work with user and his profile"""

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "bio",
            "role",
        )


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = Category
        fields = ("name", "slug")
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genres."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class WriteTitleSerializer(serializers.ModelSerializer):
    """Serializer for write request for titles."""

    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field="slug",
        queryset=Genre.objects.all(),
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = "__all__"

    def get_rating(self, obj):
        """Return 0 after creation."""
        return 0


class ReadTitleSerializer(serializers.ModelSerializer):
    """Serializer for read requests for titles."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = "__all__"
        read_only_fields = ("name", "year", "description", "genre", "category")

    def get_rating(self, obj):
        """Return object rating calculated in viewset."""
        return obj.rating


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""
    score = serializers.IntegerField(max_value=10, min_value=0)
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),  # добавил новое
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, attrs):
        """Check that each author can have only one review
        for particular title.
        """
        if not self.context["request"].method == "POST":
            return attrs
        if Review.objects.filter(
            title_id=self.context["view"].kwargs.get("title_id"),
            author=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError(
                (
                    "Автор может оставлять ревью на каждое произведение "
                    "только один раз"
                )
            )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
