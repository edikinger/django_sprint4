from django.utils.timezone import now
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponseForbidden

from .models import Category, Post, User, Comment
from .constants import FRESH_POSTS, COUNT_POSTS_ON_PAGE
from .forms import CommentForm, RegistrationForm, ProfileEditForm, PostForm
from django.views.decorators.http import require_http_methods
from django.views.generic import DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import logging

logger = logging.getLogger(__name__)

def posts_filter_by_publish(posts):
    """
    Функция возвращает набор актуальных и опубликованных постов.
    """
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now(),
    ).select_related('category', 'location', 'author')


def get_paginated_response(queryset, request, items_per_page=10):
    """
    Функция для получения пагинации
    
    :param queryset: набор объектов для пагинации
    :param request: объект запроса
    :param items_per_page: количество элементов на странице
    :return: словарь с объектами пагинации
    """
    
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # Если номер страницы не целое число, показываем первую страницу
        page_obj = paginator.page(1)
    except EmptyPage:
        # Если номер страницы выходит за пределы, показываем последнюю страницу
        page_obj = paginator.page(paginator.num_pages)
    
    paginated_data = {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'count_per_page': items_per_page
    }
    
    return paginated_data

class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        # Автор всегда имеет доступ
        if post.author == self.request.user:
            return True
        
        # Для остальных пользователей проверяем публикацию и дату
        
        return post.is_published and post.pub_date <= now()

class PostDetailView(LoginRequiredMixin, OnlyAuthorMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    
    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs.get('post_id'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author').all()
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.test_func():
            # Если пользователь не имеет права на просмотр - возвращаем 403
            return HttpResponseForbidden()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

def index(request):
    post_list = posts_filter_by_publish(Post.objects.all())[:FRESH_POSTS]
    paginator = Paginator(post_list, COUNT_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug: str):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    
    post_list = posts_filter_by_publish(category.posts.all())
    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': post_list}
    )


def user_profile(request, username: str):
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        # Для автора показываем все посты
        posts = Post.objects.filter(author=profile)
    else:
        posts = Post.objects.filter(author=profile,
            is_published=True, pub_date__lte = now()
        )
    paginator = Paginator(posts, COUNT_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user)
    else:
        form = ProfileEditForm(instance=request.user)
        
    return render(request, 'blog/user.html', {'form': form})

class ChangePasswordView(PasswordChangeView):
    success_url = reverse_lazy('profile')


@login_required
def add_comment(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post
        comment.save()
    return redirect('blog:post_detail', id=pk)

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    comment_details = {
        'comment_id': comment.id,
        'post_id': comment.post_id.id,
    }
    
    return render(
        request,
        'blog/comment.html',
        {
            'comment': comment_details,
            'form': form,
        }
    )


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post.id)  # Переадресация на страницу поста после удаления комментария
    
    return render(request, 'blog/comment.html', {'comment': comment, 'post': post})

def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('blog:index')
    else:
        form = RegistrationForm()
    return render(request, 'registration/registration_form.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Устанавливаем is_published в зависимости от даты публикации
            if post.pub_date <= now():
                post.is_published = True
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    
    return render(request, 'blog/create.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid() and post.author == request.user:
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
        elif post.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/create.html', {'form': form})

# Дополнительный view для обработки перенаправления
def login_and_redirect(request):
    next_page = request.GET.get(REDIRECT_FIELD_NAME) or reverse('blog:post_list')
    return HttpResponseRedirect(f'{reverse("login")}?{REDIRECT_FIELD_NAME}={next_page}')


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'
    
    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser
