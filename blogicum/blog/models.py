from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import User

from .constants import MAX_LENGTH_CHAR_FIELD, ABBREVIATED_TITLE


User = get_user_model()


class CreatedAt(models.Model):
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class CreatedAtIsPublished(CreatedAt):
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )

    class Meta:
        abstract = True


class Location(CreatedAtIsPublished):
    name = models.CharField(
        verbose_name="Название места",
        max_length=MAX_LENGTH_CHAR_FIELD
    )

    class Meta(CreatedAt.Meta):
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Category(CreatedAtIsPublished):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH_CHAR_FIELD)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=("Идентификатор страницы для URL;"
                   "разрешены символы латиницы, цифры, дефис и подчёркивание.")
    )

    class Meta(CreatedAt.Meta):
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:ABBREVIATED_TITLE]


class Post(CreatedAtIsPublished):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH_CHAR_FIELD)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        default=timezone.now,
        help_text=("Если установить дату и время в будущем"
                   " — можно делать отложенные публикации.")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )
    image = models.ImageField(
        'Изображение',
        upload_to='images/',
        blank=True, null=True
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        default_related_name = "posts"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title[:ABBREVIATED_TITLE]


class Comment(CreatedAt):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        verbose_name="Комментарии к посту"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации"
    )
    text = models.TextField(
        verbose_name="Текст комментария",
    )

    class Meta(CreatedAt.Meta):
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:50]
