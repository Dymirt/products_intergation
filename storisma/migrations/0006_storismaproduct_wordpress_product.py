# Generated by Django 4.2.3 on 2023-08-15 20:36

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0008_remove_wordpressproduct_attributes_and_more'),
        ('storisma', '0005_storismaproduct_storismaproductvariation'),
    ]

    operations = [
        migrations.AddField(
            model_name='storismaproduct',
            name='wordpress_product',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='storisma_product', to='wordpress.wordpressproduct'),
            preserve_default=False,
        ),
    ]
