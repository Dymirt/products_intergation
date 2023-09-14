from django.urls import path

from . import views

app_name = 'storisma'

urlpatterns = [
    path("settings", views.settings, name="settings"),
    path('create-product-variable/<int:wordpress_product_id>', views.create_product_with_variations, name="create-product"),
    path('pupulate-product-data/<int:storisma_product_id>', views.pupulate_product_data, name="populate-product"),
]