from pprint import pprint

from django.http import HttpResponseRedirect
from django.shortcuts import render
from dotenv import load_dotenv
from . import storisma
import os
import wordpress.models as wp
from . import models
from . import utils

# Create your views here.
from django.urls import reverse

load_dotenv()


STORISMA_EMAIL = os.getenv("STORISMA_EMAIL")
STORISMA_PASSWORD = os.getenv("STORISMA_PASSWORD")
STORISMA = storisma.Storisma(STORISMA_EMAIL, STORISMA_PASSWORD)
STORISMA.login()


def settings(request):
    return HttpResponseRedirect(reverse("products:products"))


def create_product_with_variations(request, wordpress_product_id):
    # Get product variations using Wordpress Api
    wordpress_product_variations = wp.WordpressProduct.objects.get(product_id=wordpress_product_id).variations

    # Group all variations attibutes and conwert them to storisma creation params dict:
    grouped_variations_attributes = wp.group_variations_attributes_by_id(
        wordpress_product_variations
    )
    storisma_super_attributes = utils.generate_storisma_super_attributes(
        grouped_variations_attributes
    )
    # Initial create product
    response = STORISMA.create_product_with_variation(
        wordpress_product_id,
        storisma_super_attributes,
    )

    # Det product id from response
    storisma_product_id = response.url.split('/')[-1]

    # Add product to storisma table to save id and associate it with worpdress product
    storisma_product = models.StorismaProduct.objects.create(
        product_id=storisma_product_id,
        wordpress_product=wp.WordpressProduct.objects.get(product_id=wordpress_product_id),
    )

    # Adding variations to
    variation_id = int(storisma_product_id) + 1
    for product_variation in wordpress_product_variations:
        variation = models.StorismaProductVariation.objects.create(
            variation_id=variation_id,
            product=storisma_product,
            stock_quantity=product_variation.get('stock_quantity'),
            price=product_variation.get('price'),
        )

        for attribute in product_variation.get('attributes'):
            storisma_attribute = models.StorismaAttribute.objects.get(wordpress_attribute__attribute_id=attribute.get('id'))
            term = models.StorismaTerm.objects.get(attribute=storisma_attribute, wordpress_term__name=attribute.get('option'))
            models.StorismaProductVariationAttribute.objects.create(
                variation=variation,
                attribute=storisma_attribute,
                term=term
            )
        variation_id += 1

    return HttpResponseRedirect(reverse("products:products"))


def pupulate_product_data(request, storisma_product_id):
    storisma_product = models.StorismaProduct.objects.get(product_id=storisma_product_id)
    STORISMA.populate_product_data(storisma_product)
    return HttpResponseRedirect(reverse("products:products"))



