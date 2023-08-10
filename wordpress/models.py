from django.db import models
from django.contrib.auth import get_user_model


class WordpressCategory(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=60)
    sku = models.DecimalField(max_digits=10, decimal_places=0)


class WordpressAttribute(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="attributes"
    )
    name = models.CharField(max_length=60)
    sku = models.DecimalField(max_digits=10, decimal_places=0)


class WordpressTerms(models.Model):
    option = models.CharField(max_length=60)
    attribute = models.ForeignKey(WordpressAttribute, on_delete=models.CASCADE, related_name="terms")


class WordpressProduct(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="products"
    )
    sku = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)
    categories = models.ManyToManyField(WordpressCategory, related_name='products')

