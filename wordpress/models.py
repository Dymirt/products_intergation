from django.db import models


class Image(models.Model):
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)


class ProductVariation(models.Model):
    ...


class WordpressProduct(models.Model):
    sku = models.DecimalField(max_digits=10, decimal_places=0)
    slug = ...
    name = ...
    short_description = ...
    description = ...
    images = models.ManyToManyField(Image)


class StorismaProduct(models.Model):
    """    'meta_title': ...,
    'meta_keywords': ...,
    'meta_description': ...,
    # Images
    # For every image
    'images[image_5]': '',  # File
    'categories[]': [],"""



class StorismaProductVariation(models.Model):
    """    # Variations, for every product variants[ variant + 1 ]
    'variants[12709][vendor_id]': ...,  # parse input variants[12709][vendor_id]
    'variants[12709][name]': ...,
    'variants[12709][color]': ...,
    'variants[12709][size]': ...,
    'variants[12709][inventories][1]': ...,
    'variants[12709][price]': ...,
    'variants[12709][weight]': ...,
    'variants[12709][status]': ...,"""