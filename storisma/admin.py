from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


# Register your models here.
@admin.register(models.StorismaCategory)
class StorismaCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", 'wordpress_category')


@admin.register(models.StorismaAttribute)
class StorismaAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'wordpress_attribute', 'display_terms')

    def display_terms(self, obj):
        categories = "<br>".join([term.name for term in obj.terms.all()])
        return mark_safe(categories)


@admin.register(models.StorismaTerm)
class StorismaTermAdmin(admin.ModelAdmin):
    list_display = ('name', 'attribute')
