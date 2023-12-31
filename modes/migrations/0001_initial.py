# Generated by Django 3.2.5 on 2021-07-20 19:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modes.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0018_auto_20210709_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionLane',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DistributionStatus',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DistributionQueue',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('claimed', models.DateTimeField(blank=True, null=True)),
                ('found', models.DateTimeField(blank=True, null=True)),
                ('assigned', models.DateTimeField(blank=True, null=True)),
                ('bpi', models.CharField(max_length=10)),
                ('bin', models.CharField(max_length=10)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dqueue_author', to=settings.AUTH_USER_MODEL)),
                ('claimer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dqueue_claimer', to=settings.AUTH_USER_MODEL)),
                ('lane', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='modes.distributionlane')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='modes.distributionstatus')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.student')),
            ],
        ),
    ]
