# Generated by Django 4.0.6 on 2022-07-11 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_personprograms_begin'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='has_case',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldevice',
            name='has_case',
            field=models.BooleanField(default=False),
        ),
    ]
