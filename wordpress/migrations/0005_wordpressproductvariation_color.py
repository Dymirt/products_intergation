# Generated by Django 4.2.3 on 2023-08-06 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0004_remove_wordpressproductvariation_colour'),
    ]

    operations = [
        migrations.AddField(
            model_name='wordpressproductvariation',
            name='color',
            field=models.CharField(default='', max_length=60),
            preserve_default=False,
        ),
    ]