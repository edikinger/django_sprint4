from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.utils.timezone import now
from django.db.models import Count
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from blog.models import Post, Category

from .models import Comment, User, Post
from .forms import CommentForm, PostForm, ProfileEditForm
from .constants import PAGINATION_COUNT_POST_PER_PAGE


class ChangePasswordView(PasswordChangeView):
    success_url = reverse_lazy('profile')


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(author=self.object)\
            .select_related('category', 'location', 'author')\
            .prefetch_related('comments')\
            .order_by('-pub_date')
        for post in posts:
            post.comment_count = post.comments.count()
        page = self.paginated_view(self.request, posts)
        context['page_obj'] = page
        context['profile'] = self.object
        return context

    def paginated_view(self, request, queryset):
        paginator = Paginator(queryset, PAGINATION_COUNT_POST_PER_PAGE)
        page_number = request.GET.get('page', 1)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return page


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        if post.author == self.request.user:
            return True
        return post.is_published and post.pub_date <= now()


class PostDetailView(LoginRequiredMixin, OnlyAuthorMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        if (
            not post.is_published
            or not post.category.is_published
            or (post.pub_date > now())
        ):
            if post.author != self.request.user:
                raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
        'author').order_by('created_at'
        ).all()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.test_func():
            return Http404
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(
        request,
        'registration/registration_form.html',
        {'form': form}
    )


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            if not request.user.is_authenticated:
                return redirect('blog:login')
            post = form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form, 'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm()
    context = {
        'form': form,
        'post': post,
        'comment': comment

    }
    return render(request, 'blog/comment.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post = get_object_or_404(Post, id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(
        request,
        'blog/comment.html',
        {
            'comment': comment,
            'form': form,
            'post': post,
        }
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        if request.user == comment.author or request.user.is_superuser:
            comment.delete()
            return redirect('blog:post_detail', post_id=post_id)
        else:
            Http404
    return render(
        request,
        'blog/comment.html',
        {'comment': comment,}
    )


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/comments.html', {'post': post})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.pub_date = now()
            post.author = request.user
            post.image = form.cleaned_data.get('image')
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


def index(request):
    post_list = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'count_per_page': paginator.per_page
    }
    return render(
        request,
        'blog/index.html',
        context
    )


def category_posts(request, category_slug: str):
    category = get_object_or_404(
            Category.objects.select_related(),
            slug=category_slug,
            is_published=True,
        )
    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(
        request,
        'blog/category.html',
        context
    )


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
