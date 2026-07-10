from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('advertise-with-us/', views.advertise_with_us, name='advertise_with_us'),
    path('editorial-policy/', views.editorial_policy, name='editorial_policy'),
    path('n/<int:pk>/', views.news_share_redirect, name='news_share_redirect'),
    path('news/<str:slug>/share-image.jpg', views.news_share_image, name='news_share_image'),
    path('news/<str:slug>/', views.news_detail, name='news_detail'),
]
