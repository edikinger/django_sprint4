from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView


handler403 = 'pages.views.error_403'
handler404 = 'pages.views.error_404'
handler500 = 'pages.views.error_500'

urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        '',
        include('blog.urls')
    ),
    path(
        'auth/registration/', 
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path(
        'pages/',
        include('pages.urls')
    ),
    path(
        'login/',
        auth_views.LoginView.as_view(),
        name='login'
    ),
    path(
        'auth/',
        include('django.contrib.auth.urls')
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
