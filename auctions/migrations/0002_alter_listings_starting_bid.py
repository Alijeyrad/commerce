# Generated by Django 3.2.7 on 2022-05-19 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='starting_bid',
            field=models.FloatField(default=0),
        ),
    ]
