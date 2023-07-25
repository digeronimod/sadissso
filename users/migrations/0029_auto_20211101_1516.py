# Generated by Django 3.2.8 on 2021-11-01 19:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_locationcode'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0028_alter_studentmodel_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentmodel',
            name='location_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.locationcode'),
        ),
        migrations.CreateModel(
            name='StudentDeviceOwnership',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.device')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.studentmodel')),
            ],
            options={
                'verbose_name': 'Student Devices',
                'verbose_name_plural': 'Student Devices',
            },
        ),
    ]
