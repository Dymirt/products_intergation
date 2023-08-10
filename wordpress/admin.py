from django.contrib import admin
from . import models
from django.utils.safestring import mark_safe


@admin.register(models.WordpressCategory)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(models.WordpressAttribute)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", 'display_options')

    def display_options(self, obj):
        terms = "<br>".join([term.option for term in obj.terms.all()])
        return mark_safe(terms)

    display_options.short_description = "Options"


@admin.register(models.WordpressTerms)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("option", "attribute")


@admin.register(models.WordpressProduct)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "display_categories")

    def display_categories(self, obj):
        categories = "<br>".join([category.name for category in obj.categories.all()])
        return mark_safe(categories)

    display_categories.short_description = "Categories"