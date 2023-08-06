from pprint import pprint

from django.shortcuts import render, reverse
from .wordpress_api import WordpressAPI
from dotenv import load_dotenv
import os
from .models import WordpressProduct, WordpressCategory
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from django.db import transaction
import logging

load_dotenv()

WP_CONSUMER_KEY = os.getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = os.getenv("WP_CONSUMER_SECRET")
WP_URL = os.getenv("WP_URL")
WORDPRESS = WordpressAPI(WP_URL, WP_CONSUMER_KEY, WP_CONSUMER_SECRET)


logger = logging.getLogger(__name__)


def category_setup(request):
    try:
        categories = WORDPRESS.get_categories()
        with transaction.atomic():
            for category in categories:
                parent_category_id = category.get('parent')
                name_rewrite = category.get('name')

                if parent_category_id:
                    try:
                        parent_category = WordpressCategory.objects.get(sku=parent_category_id)
                        parent_name_rewrite = parent_category.name
                        name_rewrite = f"{parent_name_rewrite}/{name_rewrite}"
                    except WordpressCategory.DoesNotExist:
                        logger.warning(f"Parent category with SKU {parent_category_id} not found.")
                        categories.append(category)
                        continue

                WordpressCategory.objects.create(
                    sku=category.get('id'),
                    name=name_rewrite
                )

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        return HttpResponseRedirect(reverse("products:products"))


def sync_wordpress_products(request):
    if request.user.is_authenticated:
        products = WORDPRESS.get_products()
        for product in products:
            product_obj = WordpressProduct.objects.create(
                user=request.user,
                sku=product.get('id'),
                slug=product.get('slug'),
                name=product.get('name'),
                short_description=product.get('short_description'),
                description=product.get('description'),
            )

            # Setting category ManyToManyField
            categories = [category.get("id") for category in product.get('categories')]
            product_obj.categories.set(WordpressCategory.objects.filter(sku__in=categories))
    return HttpResponseRedirect(reverse("products:products"))


class WordpressProductsListView(ListView):
    model = WordpressProduct
    template_name = "wordpress/products.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset



