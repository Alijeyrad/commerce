# Generated by Django 3.2.8 on 2022-05-23 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0016_auto_20220523_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='code',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
