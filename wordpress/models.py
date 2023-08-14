from django.db import models
from django.contrib.auth import get_user_model


class WordpressCategory(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=60)
    sku = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.name}"


class WordpressAttribute(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="attributes"
    )
    name = models.CharField(max_length=60)
    sku = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.name}"


class WordpressTerms(models.Model):
    name = models.CharField(max_length=60)
    attribute = models.ForeignKey(WordpressAttribute, on_delete=models.CASCADE, related_name="terms")

    def __str__(self):
        return f"{self.name}"


class WordpressProduct(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="products"
    )
    sku = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)
    categories = models.ManyToManyField(WordpressCategory, related_name='products')
    attributes = models.ManyToManyField(WordpressAttribute, related_name='products')

    def __str__(self):
        return f"{self.name}"
