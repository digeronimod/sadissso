# Generated by Django 3.2.8 on 2021-10-22 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20211022_1223'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalstudentmodel',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Student (Ed-Fi)'},
        ),
        migrations.AlterModelOptions(
            name='studentmodel',
            options={'ordering': ['id', 'name'], 'verbose_name': 'Student (Ed-Fi)', 'verbose_name_plural': 'Students (Ed-Fi)'},
        ),
    ]
