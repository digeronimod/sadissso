# Generated by Django 3.2.8 on 2021-10-22 17:08

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20211022_1227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalstudentmodel',
            name='foreign_status',
        ),
        migrations.RemoveField(
            model_name='historicalstudentmodel',
            name='iiq_updated',
        ),
        migrations.RemoveField(
            model_name='historicalstudentmodel',
            name='is_remote',
        ),
        migrations.RemoveField(
            model_name='historicalstudentmodel',
            name='mosyle_updated',
        ),
        migrations.RemoveField(
            model_name='historicalstudentmodel',
            name='sadis_updated',
        ),
        migrations.RemoveField(
            model_name='studentmodel',
            name='foreign_status',
        ),
        migrations.RemoveField(
            model_name='studentmodel',
            name='iiq_updated',
        ),
        migrations.RemoveField(
            model_name='studentmodel',
            name='is_remote',
        ),
        migrations.RemoveField(
            model_name='studentmodel',
            name='mosyle_updated',
        ),
        migrations.RemoveField(
            model_name='studentmodel',
            name='sadis_updated',
        ),
        migrations.AddField(
            model_name='historicalstudentmodel',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(1988, 6, 1, 8, 0)),
        ),
        migrations.AddField(
            model_name='studentmodel',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(1988, 6, 1, 8, 0)),
        ),
        migrations.AlterField(
            model_name='historicalstudentmodel',
            name='status',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='users.studentstatuses'),
        ),
        migrations.AlterField(
            model_name='studentmodel',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.studentstatuses'),
        ),
    ]