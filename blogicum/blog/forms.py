from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Comment

from .models import Post

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

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ('text',)


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='Имя',
        max_length=30,
        required=False,
        help_text='Введите ваше имя (необязательно)'
    )
    email = forms.EmailField(
        required=False,
        help_text='Введите email (необязательно)'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2', )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')