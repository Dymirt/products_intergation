# Generated by Django 4.2.3 on 2023-08-15 23:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0009_wordpressproduct_json_data_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wordpressproduct',
            name='terms',
        ),
    ]
