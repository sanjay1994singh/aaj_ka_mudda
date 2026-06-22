from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('n/<int:pk>/', views.news_share_redirect, name='news_share_redirect'),
    path('news/<str:slug>/share-image.jpg', views.news_share_image, name='news_share_image'),
    path('news/<str:slug>/', views.news_detail, name='news_detail'),
]
