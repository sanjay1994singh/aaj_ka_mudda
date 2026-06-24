from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('articles/new/', views.article_create_view, name='article_create'),
    path('articles/<int:pk>/edit/', views.article_update_view, name='article_update'),
    path('articles/<int:pk>/delete/', views.article_delete_view, name='article_delete'),
]
