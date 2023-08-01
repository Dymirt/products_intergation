from django.db import models


class ProductBase(models.Model):
    sku = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        abstract = True


class WordpressProduct(ProductBase):
    ...


class StorismaProduct(ProductBase):
    ...
