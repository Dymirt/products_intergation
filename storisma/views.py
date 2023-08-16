from django.http import HttpResponseRedirect
from django.shortcuts import render
from dotenv import load_dotenv
from . import storisma
import os
from wordpress.models import WordpressAttribute, WordpressProduct
from wordpress.wordpress_api import wp
from . import models

# Create your views here.
from django.urls import reverse

load_dotenv()


STORISMA_EMAIL = os.getenv("STORISMA_EMAIL")
STORISMA_PASSWORD = os.getenv("STORISMA_PASSWORD")
STORISMA = storisma.Storisma(STORISMA_EMAIL, STORISMA_PASSWORD)
response = STORISMA.login()


def settings(request):
    return HttpResponseRedirect(reverse("products:products"))


def create_product_with_variations(request, wordpress_product_id):
    # Get product variations using Wordpress Api
    wordpress_product_variations = WordpressProduct.objects.get(product_id=wordpress_product_id).variations_in_stock

    # Group all variations attibutes and conwert them to storisma creation params dict:
    grouped_variations_attributes = group_wordpress_attributes(
        wordpress_product_variations
    )
    storisma_super_attributes = wordpress_to_storisma_atributes(
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
        wordpress_product=WordpressProduct.objects.get(product_id=wordpress_product_id),
    )

    # Adding variations to
    variation_id = int(storisma_product_id) + 1
    for _ in wordpress_product_variations:
        models.StorismaProductVariation.objects.create(
            variation_id=variation_id,
            product=storisma_product,
        )
        variation_id += 1

    return HttpResponseRedirect(reverse("products:products"))


def pupulate_product_data(request, storisma_product_id):
    #TODO
    return HttpResponseRedirect(reverse("products:products"))


def wordpress_to_storisma_atributes(grouped_variations_attributes: list) -> dict:
    storisma_super_attributes = {}
    # Convert the variation terms for storisma
    for attribute in grouped_variations_attributes:
        # Get Wordpress attribute asociated with storisma attribute
        wordpress_attribute_object = WordpressAttribute.objects.get(
            attribute_id=attribute.get("attribute_id")
        )
        # Get first asociated storisma attribute name
        storisma_attribute_name = (
            wordpress_attribute_object.storisma_attributes.first().name
        )
        # Get asociated storisma options
        storisma_terms = models.StorismaTerm.objects.filter(
            wordpress_term__name__in=attribute.get("options")
        )

        # Get list of storisma term names
        storisma_terms_name_list = [str(term.term_id) for term in storisma_terms]

        storisma_super_attributes[
            f"super_attributes[{storisma_attribute_name}][]"
        ] = storisma_terms_name_list

    return storisma_super_attributes


def group_wordpress_attributes(variations: list) -> list:
    attribute_groups = {}  # Use this dictionary to keep track of groups by attribute_id

    for variation in variations:
        for attribute in variation.get('attributes'):
            attribute_id = attribute.get("id")
            option = attribute.get("option")

            if attribute_id in attribute_groups:
                attribute_groups[attribute_id]["options"].add(option)
            else:
                attribute_groups[attribute_id] = {
                    "attribute_id": attribute_id,
                    "options": {option},
                }

    return list(attribute_groups.values())
