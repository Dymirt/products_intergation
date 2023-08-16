from django.db import models
from django.contrib.auth import get_user_model
from .wordpress_api import wp


class WordpressCategory(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=60)
    category_id = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.name}"


class WordpressAttribute(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="attributes"
    )
    name = models.CharField(max_length=60)
    attribute_id = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.name}"


class WordpressTerms(models.Model):
    name = models.CharField(max_length=60)
    attribute = models.ForeignKey(WordpressAttribute, on_delete=models.CASCADE, related_name="terms")

    def __str__(self):
        return f"{self.attribute.name}-{self.name}"


class WordpressProduct(models.Model):
    class Meta:
        ordering = ['product_id']

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="products"
    )
    product_id = models.DecimalField(max_digits=10, decimal_places=0)
    categories = models.ManyToManyField(WordpressCategory, related_name='products')
    json_data = models.JSONField()
    variations_json_data = models.JSONField()

    def __str__(self):
        return f"{self.name}"

    @property
    def slug(self):
        return self.json_data.get('slug')

    @property
    def short_description(self):
        return self.json_data.get('short_description')

    @property
    def description(self):
        return self.json_data.get('description')

    @property
    def name(self):
        return self.json_data.get('name')

    @property
    def variations(self):
        if self.variations_json_data:
            return self.variations_json_data
        else:
            self.variations_json_data = wp.products.get(self.product_id).variations.all()
            self.save()
        return self.variations

    @property
    def variations_in_stock(self):
        return list(filter(lambda variation: variation.get('stock_quantity') > 0, self.variations))
