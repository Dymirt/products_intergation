# Generated by Django 4.2.3 on 2023-09-15 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storisma', '0010_remove_storismaproductvariation_attributes_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StorismaProductAttribute',
            new_name='StorismaProductVariationAttribute',
        ),
    ]
