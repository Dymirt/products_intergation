from django.db import models
import wordpress.models as wordpress
from . import data


class StorismaAttribute(models.Model):
    name = models.CharField(max_length=60)
    wordpress_attribute = models.ForeignKey(
        wordpress.WordpressAttribute,
        on_delete=models.SET_NULL,
        related_name='storisma_attributes',
        null=True
    )

    def __str__(self):
        return f"{self.name}"


class StorismaTerm(models.Model):
    term_id = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)
    attribute = models.ForeignKey('StorismaAttribute', on_delete=models.CASCADE, related_name="terms")
    wordpress_term = models.ForeignKey(
        'wordpress.WordpressTerms',
        on_delete=models.SET_NULL,
        related_name='storisma_terms',
        null=True
    )

    def __str__(self):
        return f"{self.name}"


class StorismaCategory(models.Model):
    category_id = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)
    wordpress_category = models.ManyToManyField(
        wordpress.WordpressCategory,
        related_name='storisma_categories',
    )

    def __str__(self):
        return f"{self.name}"


class StorismaProduct(models.Model):
    product_id = models.DecimalField(max_digits=10, decimal_places=0)
    wordpress_product = models.OneToOneField(wordpress.WordpressProduct, on_delete=models.CASCADE, related_name='storisma_product')


class StorismaProductVariation(models.Model):
    variation_id = models.DecimalField(max_digits=10, decimal_places=0)
    product = models.ForeignKey(StorismaProduct, on_delete=models.CASCADE, related_name="variations")


# Populate YourModel using data from the data.py file
def populate_category_model_from_data():
    for category in data.categories:
        StorismaCategory.objects.create(
            category_id=category.get('category_id'),
            name=category.get('name')
        )


def populate_attributes_model_from_data():
    for attribute in data.attributes:
        attribute_obj = StorismaAttribute.objects.create(
            name=attribute.get('name')
        )
        populate_attribute_terms_model_from_data(attribute_obj, attribute.get('terms'))


def populate_attribute_terms_model_from_data(attribute, attribute_terms_data):
    for term in attribute_terms_data:
        StorismaTerm.objects.create(
            term_id=term.get('term_id'),
            name=term.get('name'),
            attribute=attribute
        )


def populate_models_from_data():
    populate_category_model_from_data()
    populate_attributes_model_from_data()