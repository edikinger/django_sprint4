from django.urls import path, include
from . import views
app_name = 'blog'


urlpatterns = [
    path('', views.index, name='index'),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts, name='category_posts'
    ),
    path(
        'auth/',
        include('django.contrib.auth.urls')
    ),
    path('profile/<str:username>/',
        views.ProfileDetailView.as_view(),
        name='profile'
    ),
    path(
        'edit_profile/',
        views.edit_profile,
        name='edit_profile'
    ),
    path(
        'password_change/',
        views.ChangePasswordView.as_view(),
        name='password_change'
    ),
    path(
        'posts/<int:post_id>/comment/',
          views.add_comment,
          name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment, name='delete_comment'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.delete_post,
        name='delete_post'
    ),
    path(
        'posts/create/',
        views.create_post,
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.edit_post,
        name='edit_post'
    ),
]
