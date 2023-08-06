from django.contrib import admin
from . import models
from django.utils.safestring import mark_safe


@admin.register(models.WordpressCategory)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("sku", "name")


@admin.register(models.WordpressProduct)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "display_categories")

    def display_categories(self, obj):
        categories = "<br>".join([category.name for category in obj.categories.all()])
        return mark_safe(categories)

    display_categories.short_description = "Categories"