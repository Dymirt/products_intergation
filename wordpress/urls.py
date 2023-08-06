from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path("sync/", views.sync_wordpress_products, name="sync_products"),
    path('', views.WordpressProductsListView.as_view(), name="products"),
]