from django.urls import path

from . import views


app_name = "epaper"

urlpatterns = [
    path("", views.epaper_home, name="home"),
    path("upload/", views.upload_epaper, name="upload"),
    path("edition/<int:pk>/", views.epaper_home, name="edition"),
]
