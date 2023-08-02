from django.shortcuts import render, reverse
from .wordpress_api import WordpressAPI
from dotenv import load_dotenv
import os
from .models import WordpressProduct
from django.views.generic import ListView
from django.http import HttpResponseRedirect


load_dotenv()

WP_CONSUMER_KEY = os.getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = os.getenv("WP_CONSUMER_SECRET")
WP_URL = os.getenv("WP_URL")


# Create your views here.
def sync_wordpress_products(request):
    if request.user.is_authenticated:
        wp = WordpressAPI(WP_URL, WP_CONSUMER_KEY, WP_CONSUMER_SECRET)
        products = wp.get_products()
        for product in products:
            WordpressProduct.objects.create(
                user=request.user,
                sku=product.get('id'),
                slug=product.get('slug'),
                name=product.get('name'),
                short_description=product.get('short_description'),
                description=product.get('description'),
            )
    return HttpResponseRedirect(reverse("products:products"))


class WordpressProductsListView(ListView):
    model = WordpressProduct
    template_name = "wordpress/products.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

