from django import forms
from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'category', 'location', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
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


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
