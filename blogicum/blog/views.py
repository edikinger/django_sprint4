from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import DetailView, ListView

from .constants import PAGINATION_COUNT_POST_PER_PAGE
from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post, User


def posts_filter_by_publish(posts):
    """Функция возвращает набор актуальных и опубликованных постов."""
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now(),
    ).select_related('category', 'location', 'author')


def annotate_posts(queryset):
    """Добавляет к QuerySet аннотацию c количеством комментариев."""
    return queryset.annotate(comment_count=Count('comments'))


def paginate_queryset(
        queryset,
        request,
        per_page=PAGINATION_COUNT_POST_PER_PAGE
    ):
    """Функция для пагинации QuerySet."""
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return {
        'page_obj': page_obj
    }


class ProfileDetailView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = PAGINATION_COUNT_POST_PER_PAGE


    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        queryset = author.posts.all()
        queryset = annotate_posts(queryset)
        if self.request.user != author:
            queryset = posts_filter_by_publish(queryset)
        return queryset.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        if self.request.user == post.author:
            return post
        else:
            filtered_posts = posts_filter_by_publish(Post.objects.all())
            return get_object_or_404(filtered_posts, pk=self.kwargs.get('post_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author').order_by('created_at')
        return context


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if form.is_valid():
        post = form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form, 'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'comment': comment

    }
    return render(request, 'blog/comment.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        'blog/comment.html',
        {
            'comment': comment,
            'form': form,
            'post': comment.post,
        }
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author or request.user.is_superuser:
        if request.method == 'POST':
            comment.delete()
            return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        'blog/comment.html',
        {'comment': comment}
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
    form = PostForm(request.POST or None, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


def index(request):
    post_list = posts_filter_by_publish(Post.objects.all()).order_by('-pub_date')
    post_list = annotate_posts(post_list)
    context = paginate_queryset(post_list, request)
    return render(
        request,
        'blog/index.html',
        context
    )


def category_posts(request, category_slug: str):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    all_posts = category.posts.all()
    filtered_posts = posts_filter_by_publish(all_posts)
    post_list = annotate_posts(filtered_posts)
    post_list = post_list.order_by('-pub_date')
    pagination_context = paginate_queryset(post_list, request)
    context = {
        'category': category,
        **pagination_context
    }
    return render(
        request,
        'blog/category.html',
        context
    )


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', {'form': form})
