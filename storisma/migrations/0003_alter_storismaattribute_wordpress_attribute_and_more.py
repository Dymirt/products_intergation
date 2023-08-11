# Generated by Django 4.2.3 on 2023-08-11 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0003_wordpressattribute_sku'),
        ('storisma', '0002_alter_storismacategory_wordpress_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storismaattribute',
            name='wordpress_attribute',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='storisma_attributes', to='wordpress.wordpressattribute'),
        ),
        migrations.AlterField(
            model_name='storismacategory',
            name='wordpress_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='storisma_categories', to='wordpress.wordpresscategory'),
        ),
        migrations.AlterField(
            model_name='storismaterm',
            name='wordpress_term',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='storisma_terms', to='wordpress.wordpressterms'),
        ),
    ]
