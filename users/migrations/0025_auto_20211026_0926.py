# Generated by Django 3.2.8 on 2021-10-26 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20211022_1308'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalstudentmodel',
            old_name='fleid',
            new_name='unique_id',
        ),
        migrations.RenameField(
            model_name='studentmodel',
            old_name='fleid',
            new_name='unique_id',
        ),
    ]