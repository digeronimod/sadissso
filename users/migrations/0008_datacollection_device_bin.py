# Generated by Django 3.2 on 2021-05-04 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_studentfinesexport'),
    ]

    operations = [
        migrations.AddField(
            model_name='datacollection',
            name='device_bin',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
