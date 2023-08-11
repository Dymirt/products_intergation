from django.urls import path

from . import views

app_name = 'storisma'

urlpatterns = [
    path("", views.storisma, name="sync_products"),
]