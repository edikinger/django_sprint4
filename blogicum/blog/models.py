from django.db import models
from django.contrib.auth import get_user_model
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


class Location(CreatedAtIsPublished):
    name = models.CharField(
        verbose_name="Название места",
        max_length=MAX_LENGTH_CHAR_FIELD
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name[:ABBREVIATED_TITLE]


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
        "Дата и время публикации",
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
        verbose_name="Категория"
    )
    image = models.ImageField('Изображение', upload_to='images/', null=True, blank=True)

    @property
    def has_image(self):
        return self.image and self.image.name

    @property
    def comment_count(self):
        return self.comments.count()
    

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        default_related_name = "posts"
        ordering = ("-pub_date",)
    
    def __str__(self):
        return self.title[:ABBREVIATED_TITLE]


class Comment(models.Model):
    text = models.TextField("Текст")
    post_id = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name = "comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("created_at",)
    
    def __str__(self):
        return f"Комментарий от {self.author} к посту {self.post_id}"
