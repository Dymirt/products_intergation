from django.urls import path

from . import views

app_name = 'storisma'

urlpatterns = [
    path("settings", views.settings, name="settings"),
]