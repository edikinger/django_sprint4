from django.core.paginator import Paginator
from django.db.models import Count
from django.utils.timezone import now

from .constants import PAGINATION_COUNT_POST_PER_PAGE


def posts_filter_by_publish(posts):
    """Функция возвращает набор актуальных и опубликованных постов."""
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now(),
    )


def annotate_posts(queryset):
    """Добавляет к QuerySet аннотацию c количеством комментариев."""
    return queryset.annotate(
        comment_count=Count('comments')
    ).select_related(
        'category',
        'location',
        'author'
    ).order_by(
        '-pub_date'
    )


def paginate_queryset(
    queryset,
    request,
    per_page=PAGINATION_COUNT_POST_PER_PAGE
):
    """Функция для пагинации QuerySet."""
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    return paginator.get_page(page)
