# Generated by Django 3.2.8 on 2022-05-23 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_remove_listing_bids'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='bids',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auctions.bid'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='image_url',
            field=models.URLField(),
        ),
    ]