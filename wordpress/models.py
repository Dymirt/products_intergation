from django.db import models
from django.contrib.auth import get_user_model


class WordpressImage(models.Model):
    product = models.ForeignKey("WordpressProduct", on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)


class WordpressCategory(models.Model):
    sku = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)


class WordpressProductVariation(models.Model):
    product = models.ForeignKey("WordpressProduct", on_delete=models.CASCADE, related_name="variations")
    sku = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)
    size = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.DecimalField(max_digits=3, decimal_places=0)
    color = models.CharField(max_length=60)


class WordpressProduct(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="products"
    )
    sku = models.DecimalField(max_digits=10, decimal_places=0)
    slug = models.CharField(max_length=60)
    name = models.CharField(max_length=60)
    short_description = models.TextField()
    description = models.TextField()
    categories = models.ManyToManyField(WordpressCategory, related_name='products')

