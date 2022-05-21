# Generated by Django 3.2.7 on 2022-05-19 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bids',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid', models.FloatField()),
                ('time_added', models.DateTimeField(auto_now_add=True)),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('for_listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.listings')),
            ],
        ),
    ]