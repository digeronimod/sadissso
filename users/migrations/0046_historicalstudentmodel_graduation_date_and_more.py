# Generated by Django 4.0.2 on 2022-05-11 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0045_delete_studentprograms'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalstudentmodel',
            name='graduation_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentmodel',
            name='graduation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
