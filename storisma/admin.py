from django.contrib import admin
from django.utils.safestring import mark_safe
from . import forms
import wordpress.models as wordpress
from . import models


# Register your models here.
@admin.register(models.StorismaCategory)
class StorismaCategoryAdmin(admin.ModelAdmin):
    list_filter = ["wordpress_category__user__username"]
    list_display = ("name", "display_wordpress_category")

    def display_wordpress_category(self, obj):
        wordpress_category = "<br>".join(
            [category.name for category in obj.wordpress_category.all()]
        )
        return mark_safe(wordpress_category)


@admin.register(models.StorismaAttribute)
class StorismaAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "wordpress_attribute", "display_terms")

    def display_terms(self, obj):
        categories = "<br>".join([term.name for term in obj.terms.all()])
        return mark_safe(categories)


@admin.register(models.StorismaTerm)
class StorismaTermAdmin(admin.ModelAdmin):
    form = forms.StorismaTermAdminForm
    list_display = ("name", "wordpress_term", "attribute")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Modify the queryset for the wordpress_term field
        if obj and "wordpress_term" in form.base_fields:
            related_attribute = obj.attribute
            if related_attribute:
                related_attribute_terms = wordpress.WordpressTerms.objects.filter(
                    attribute__storisma_attributes=related_attribute
                )
                form.base_fields["wordpress_term"].queryset = related_attribute_terms
            else:
                form.base_fields[
                    "wordpress_term"
                ].queryset = wordpress.WordpressTerms.objects.none()
        return form


@admin.register(models.StorismaProduct)
class StorismaProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "wordpress_product")


@admin.register(models.StorismaProductVariationAttribute)
class StorismaProductVariationAttributeAdmin(admin.ModelAdmin):
    list_display = ("variation", "attribute", "term")


@admin.register(models.StorismaProductVariation)
class StorismaProductVariationAdmin(admin.ModelAdmin):
    list_display = ("variation_id", "product__wordpress_product", 'price', 'stock_quantity', 'attributes')

    def product__wordpress_product(self, obj):
        return obj.product.wordpress_product

    product__wordpress_product.short_description = "WordPress Product"
