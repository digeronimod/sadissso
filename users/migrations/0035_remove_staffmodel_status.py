# Generated by Django 3.2.8 on 2021-11-22 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_staffmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffmodel',
            name='status',
        ),
    ]
