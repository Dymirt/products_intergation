from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('category_setup', views.category_setup, name='category_setup'),
    path("sync/", views.sync_wordpress_products, name="sync_products"),
    path('', views.WordpressProductsListView.as_view(), name="products"),
]