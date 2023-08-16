from django.shortcuts import reverse
from .wordpress_api import WordpressAPI
from dotenv import load_dotenv
import os
from . import models
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


def sync_products(request):
    if request.user.is_authenticated:
        products = WORDPRESS.products.all()
        for product in products:
            product_obj = models.WordpressProduct.objects.create(
                user=request.user,
                product_id=product.get('id'),
                json_data=product
            )
            logger.warning(f"Product {product_obj.product_id} created.")

            # Setting category ManyToManyField
            categories = [category.get("id") for category in product.get('categories')]
            product_obj.categories.set(models.WordpressCategory.objects.filter(category_id__in=categories))

    return HttpResponseRedirect(reverse("products:products"))


def sync_categories(request):
    categories = WORDPRESS.categories.all()

    with transaction.atomic():
        for category in categories:
            parent_category_id = category.get('parent')
            name_rewrite = category.get('name')

            if parent_category_id:
                try:
                    parent_category = models.WordpressCategory.objects.get(category_id=parent_category_id)
                    parent_name_rewrite = parent_category.name
                    name_rewrite = f"{parent_name_rewrite}/{name_rewrite}"
                except models.WordpressCategory.DoesNotExist:
                    logger.warning(f"Parent category with SKU {parent_category_id} not found.")
                    categories.append(category)
                    continue

            models.WordpressCategory.objects.create(
                user=request.user,
                category_id=category.get('id'),
                name=name_rewrite
            )

    return HttpResponseRedirect(reverse("products:products"))


def sync_attributes(request):
    attributes = WORDPRESS.attributes.all()
    for attribute in attributes:
        attribute = models.WordpressAttribute.objects.create(
            user=request.user,
            name=attribute.get('name'),
            attribute_id=attribute.get('id'),
        )
        sync_attribute_terms(attribute)

    return HttpResponseRedirect(reverse("products:products"))


def sync_attribute_terms(attribute):
    terms = WORDPRESS.attributes.terms(attribute.sku).all()
    for term in terms:
        models.WordpressTerms.objects.create(
            attribute=attribute,
            option=term.get("name")
        )


class WordpressProductsListView(ListView):
    model = models.WordpressProduct
    template_name = "wordpress/products.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset





