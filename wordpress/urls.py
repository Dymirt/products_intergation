from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path("sync/", views.sync_products, name="sync_products"),
    path('', views.WordpressProductsListView.as_view(), name="products"),
    path('categories/sync', views.sync_categories, name='sync_categories'),
    path('attributes/sync', views.sync_attributes, name="sync_attributes"),
]