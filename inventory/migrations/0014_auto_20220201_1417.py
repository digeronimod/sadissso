# Generated by Django 3.2.8 on 2022-02-01 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_devicehistorydata_author_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceassessment',
            name='device_damage_prt',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='historicaldeviceassessment',
            name='device_damage_prt',
            field=models.BooleanField(default=0),
        ),
    ]
