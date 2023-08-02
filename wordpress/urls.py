from django.urls import path
from .views import WordpressProductsListView, sync_wordpress_products

app_name = 'products'

urlpatterns = [
    path("sync/", sync_wordpress_products, name="sync_products"),
    path('', WordpressProductsListView.as_view(), name="products"),
]