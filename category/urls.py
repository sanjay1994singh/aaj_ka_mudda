from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.category_news, name='category_news'),
]