from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [

    path('', views.home, name='home'),

    path('news/<slug:slug>/', views.news_detail, name='news_detail'),

    path('category/<slug:slug>/', views.category_news, name='category_news'),

    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),

    path('contact/', views.contact, name='contact'),

    path(
        'privacy-policy/',
        views.privacy_policy,
        name='privacy_policy'
    ),

    path(
        'disclaimer/',
        views.disclaimer,
        name='disclaimer'
    ),

    path(
        'terms-and-conditions/',
        views.terms,
        name='terms'
    ),
]

urlpatterns += [

    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain'
        )
    ),

]
