# Generated by Django 3.2.13 on 2023-02-07 20:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_auto_20220815_0856'),
        ('users', '0051_studentmodelidlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newdatacollection',
            name='student_next_grade',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='newdatacollection',
            name='student_next_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.location'),
        ),
    ]
