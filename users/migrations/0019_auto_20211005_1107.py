# Generated by Django 3.2.5 on 2021-10-05 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20210709_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalstudent',
            name='fleid',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='fleid',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
