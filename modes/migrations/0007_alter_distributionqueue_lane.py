# Generated by Django 3.2.5 on 2021-07-22 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modes', '0006_distributionlane_members'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributionqueue',
            name='lane',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='modes.distributionlane'),
        ),
    ]
