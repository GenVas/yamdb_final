from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class UserRole:
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


ROLE_CHOICES = (
    (UserRole.USER, "пользователь"),
    (UserRole.MODERATOR, "модератор"),
    (UserRole.ADMIN, "администратор"),
)


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name="имя пользователя",
        max_length=150,
        unique=True,
        help_text="Необходимые. 150 символов или меньше.",
        validators=[username_validator],
        error_messages={
            "unique": "Пользователь с таким именем уже существует.",
        },
    )
    first_name = models.CharField(
        verbose_name="имя",
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name="фамилия",
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        verbose_name="адрес электронной почты",
        blank=False,
        unique=True,
        max_length=254,
    )
    bio = models.TextField(verbose_name="пару слов о себе", blank=True)
    role = models.CharField(
        verbose_name="роль",
        max_length=60,
        choices=ROLE_CHOICES,
        null=False,
        default=UserRole.USER,
    )

    REQUIRED_FIELDS = ["email"]

    class Meta:

        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        constraints = [
            models.CheckConstraint(
                check=~Q(username="me"),
                name="Пользователь не может быть назван me!",
            )
        ]

    def __str__(self):
        return f"{self.username} is a {self.role}"


class Category(models.Model):
    """Model for categories."""

    name = models.CharField(
        verbose_name="название",
        max_length=256,
        unique=True,
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name[:30]


class Genre(models.Model):
    """Model for genres."""

    name = models.CharField(
        verbose_name="название жанра",
        max_length=256,
        unique=True,
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "жанр"
        verbose_name_plural = "жанры"

    def __str__(self):
        return self.name[:30]


class Title(models.Model):
    """Model for titles."""

    name = models.CharField(
        verbose_name="название произведения",
        help_text='Введите название произведения',
        max_length=300,
        blank=False,
    )
    year = models.IntegerField(
        verbose_name="год выпуска произведения",
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(datetime.now().year),
        ],
    )
    description = models.TextField(
        max_length=400,
        verbose_name="описание произведения",
        default="описание не предоставлено",
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',  # added new
        verbose_name="жанр произведения",
        # through="GenreTitle",
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name="категория произведения",
        on_delete=models.SET_NULL,
        related_name="titles",
        null=True,
    )

    class Meta:
        verbose_name = "произведение"
        verbose_name_plural = "произведения"
        ordering = ['year']

    def __str__(self):
        return self.name

# class GenreTitle(models.Model):
#     """Through this model Genre and Title models ale linked."""

#     title = models.ForeignKey(Title, on_delete=models.CASCADE)
#     genre = models.ForeignKey(Genre, on_delete=models.CASCADE)


class Review(models.Model):
    """Model for reviews.
    `title` - one-to-many relation with Title model.
    `author` - one-to-one relation with Review model.
    """

    text = models.TextField(
        max_length=400,
        verbose_name="Текст ревью"
    )
    title = models.ForeignKey(
        Title,
        related_name="reviews",
        on_delete=models.CASCADE,
        verbose_name="ревью конкретного произведения",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="ревью конкретного автора",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="оценка произведения",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        default=0,
        blank=False,
        null=False
    )
    pub_date = models.DateTimeField(
        verbose_name="дата публикации",
        # default=datetime.now,
        db_index=True,
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Ревью"
        verbose_name_plural = "Ревью"
        constraints = [
            models.UniqueConstraint(
                fields=("author", "title"),
                name="unique author`s review for each title",
            )
        ]

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
    """Model for comments.
    `review` - one-to-many relation with Review model.
    `author` - one-to-many relation with User model.
    """

    text = models.TextField(verbose_name="Текст комментария")
    review = models.ForeignKey(
        Review,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="комментарии конкретного ревью",
    )
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="комментарии конкретного автора",
    )
    pub_date = models.DateTimeField(
        verbose_name="дата публикации",
        # default=datetime.now,
        db_index=True,
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['pub_date']

    def __str__(self):
        return self.text[:30]
