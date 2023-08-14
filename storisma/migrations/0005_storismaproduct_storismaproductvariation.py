# Generated by Django 4.2.3 on 2023-08-14 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storisma', '0004_remove_storismacategory_wordpress_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StorismaProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.DecimalField(decimal_places=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='StorismaProductVariation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variation_id', models.DecimalField(decimal_places=0, max_digits=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variations', to='storisma.storismaproduct')),
            ],
        ),
    ]
