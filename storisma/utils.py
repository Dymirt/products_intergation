from django.shortcuts import get_list_or_404, get_object_or_404
from .models import StorismaTerm
from wordpress.models import WordpressAttribute


def generate_storisma_super_attributes(grouped_variations_attributes: list) -> dict:
    storisma_super_attributes = {}

    for attribute in grouped_variations_attributes:
        attribute_id = attribute.get("attribute_id")
        options = attribute.get("options")

        # Get Wordpress attribute associated with storisma attribute
        wordpress_attribute_object = get_object_or_404(
            WordpressAttribute, attribute_id=attribute_id
        )

        # Get the first associated storisma attribute name
        storisma_attribute = wordpress_attribute_object.storisma_attributes.first()
        if storisma_attribute:
            storisma_attribute_name = storisma_attribute.name

            # Get associated storisma terms
            storisma_terms = get_list_or_404(
                StorismaTerm, wordpress_term__name__in=options
            )

            # Get list of storisma term names
            storisma_terms_name_list = [str(term.term_id) for term in storisma_terms]

            storisma_super_attributes[
                f"super_attributes[{storisma_attribute_name}][]"
            ] = storisma_terms_name_list

    return storisma_super_attributes