# Generated by Django 3.2.8 on 2022-05-21 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_category_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='image',
        ),
    ]
