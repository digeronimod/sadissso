# Generated by Django 3.2.8 on 2021-10-29 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_studentmodel_location_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentmodel',
            name='unique_id',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]