# Generated by Django 3.2 on 2021-05-26 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_datacollection_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalstudent',
            name='birthdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
