# Generated by Django 3.2.8 on 2021-11-02 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_locationcode'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HistoricalCharger',
        ),
    ]
