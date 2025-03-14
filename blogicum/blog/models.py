from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import User

from .constants import MAX_LENGTH_CHAR_FIELD, ABBREVIATED_TITLE


User = get_user_model()

class CreatedAtIsPublished(models.Model):
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        abstract = True


class Location(models.Model):
    name = models.CharField(max_length=255)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(CreatedAtIsPublished):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH_CHAR_FIELD)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=("Идентификатор страницы для URL; "
                   "разрешены символы латиницы, цифры, дефис и подчёркивание.")
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:ABBREVIATED_TITLE]


class Post(CreatedAtIsPublished):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH_CHAR_FIELD)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
    default=timezone.now,
    help_text="Выберите дату публикации")
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
    image = models.ImageField('Изображение', upload_to='images/', blank=True, null=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        default_related_name = "posts"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.title[:ABBREVIATED_TITLE]

    @property
    def comments_count(self):
        return self.comments.count()

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]
