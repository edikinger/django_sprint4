from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/',views.PostDetailView.as_view(), name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts, name='category_posts'
    ),
    path('profile/<str:username>', views.user_profile, name='profile' ),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('password_change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('posts/create/', views.create_post, name='create_post' ),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('posts/<int:post_id>/delete_post/', views.DeletePostView.as_view(), name='delete_post')
]



# from django.urls import path

# from news import views

# app_name = 'news'

# urlpatterns = [
#     path('', views.NewsList.as_view(), name='home'),
#     path('news/<int:pk>/', views.NewsDetailView.as_view(), name='detail'),
#     path(
#         'delete_comment/<int:pk>/',
#         views.CommentDelete.as_view(),
#         name='delete'
#     ),
#     path('edit_comment/<int:pk>/', views.CommentUpdate.as_view(), name='edit'),
# ]