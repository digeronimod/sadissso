# Generated by Django 3.2.3 on 2021-06-01 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_historicalstudent_birthdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalstudent',
            name='birthdate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
