from django_filters import rest_framework as filters

from reviews.models import Category, Genre, Title


class CategoriesFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Category
        fields = ['name']


class GenresFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Genre
        fields = ['name']


class TitleFilter(filters.FilterSet):
    """Filter for title.
    `category` & `genre` filters via slug.
    """

    name = filters.CharFilter(
        field_name="name", lookup_expr="contains"
    )
    category = filters.CharFilter(
        field_name="category__slug", lookup_expr="contains"
    )
    genre = filters.CharFilter(
        field_name="genre__slug", lookup_expr="contains"
    )

    class Meta:
        model = Title
        fields = (
            "name",
            "category",
            "genre",
            "year",
        )
