from pprint import pprint

from django.shortcuts import render, reverse
from .wordpress_api import WordpressAPI
from dotenv import load_dotenv
import os
from .models import WordpressProduct, WordpressCategory, WordpressProductVariation
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


def category_setup():
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


def is_size_attribute(attributes_id):
    return attributes_id.get('id') == 1


def is_color_attribute(attributes_id):
    return attributes_id.get('id') == 4


def sync_wordpress_products(request):
    category_setup()
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
            logger.warning(f"Product {product_obj.sku} created.")

            # Setting category ManyToManyField
            categories = [category.get("id") for category in product.get('categories')]
            product_obj.categories.set(WordpressCategory.objects.filter(sku__in=categories))

            for variation_id in product.get('variations'):
                variation = WORDPRESS.get_product_variation(product.get('id'), variation_id)
                stock_quantity = variation.get('stock_quantity')

                attributes = variation.get('attributes')
                size_attribute = list(filter(is_size_attribute, attributes))[0].get('option')
                try:
                    color_attribute = list(filter(is_color_attribute, attributes))[0].get('option')
                except IndexError:
                    color_attribute = ''

                if stock_quantity:
                    variation_obj = WordpressProductVariation.objects.create(
                        product=product_obj,
                        sku=variation.get("id"),
                        name=f"{product_obj.name} - {size_attribute} {color_attribute}",
                        size=size_attribute,
                        price=variation.get('price'),
                        stock_quantity=stock_quantity,
                        color=color_attribute
                    )
                    logger.warning(f"Product {product.get('id')} variation {variation_obj.sku} created.")

    return HttpResponseRedirect(reverse("products:products"))


def sync_products_variations(product: WordpressProduct):
    product_variations = WORDPRESS.get_product_variations(product.sku)
    for variation in product_variations:
        stock_quantity = variation.get('stock_quantity')
        size = variation.get('attributes')[0].get('option')
        if stock_quantity:
            variation_obj = WordpressProductVariation.objects.create(
                product=product,
                sku=variation.get("id"),
                name=f"{product.name} - {size}",
                size=size,
                price=variation.get('price'),
                stock_quantity=stock_quantity,
            )
            logger.warning(f"Product {product.sku} variation {variation_obj.sku} created.")


class WordpressProductsListView(ListView):
    model = WordpressProduct
    template_name = "wordpress/products.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset



