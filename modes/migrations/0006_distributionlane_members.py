# Generated by Django 3.2.5 on 2021-07-22 17:14

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('modes', '0005_alter_distributionqueue_bpi'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributionlane',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
