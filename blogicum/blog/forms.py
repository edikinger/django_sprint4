from django import forms
from django.utils import timezone

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author','is_published', 'created_date',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'pub_date': 'Дата и время публикации',
            'category': 'Категория',
            'location': 'Местоположение',
            'image': 'Изображение',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now().astimezone()
        formatted_date = now.isoformat()[:16]
        self.initial['pub_date'] = formatted_date

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
