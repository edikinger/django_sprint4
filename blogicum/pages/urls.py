from django.urls import path

from pages.views import AboutView, RulesView

app_name = 'pages'

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('contacts/', RulesView.as_view(), name='rules'),
]
