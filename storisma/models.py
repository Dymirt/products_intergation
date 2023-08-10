from django.db import models


class StorismaAttribute(models.Model):
    name = ...


class StorismaTerm(models.Model):
    term_id = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)
    attribute = models.ForeignKey(StorismaAttribute, on_delete=models.CASCADE, related_name="terms")


class StorismaCategory(models.Model):
    category_id = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=60)