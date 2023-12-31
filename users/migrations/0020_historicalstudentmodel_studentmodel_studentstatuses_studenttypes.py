# Generated by Django 3.2.8 on 2021-10-22 16:21

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0009_calendlyevent_event_name'),
        ('users', '0019_auto_20211005_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentStatuses',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Student Status',
                'verbose_name_plural': 'Student Statuses',
            },
        ),
        migrations.CreateModel(
            name='StudentTypes',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Student Type',
                'verbose_name_plural': 'Student Types',
            },
        ),
        migrations.CreateModel(
            name='StudentModel',
            fields=[
                ('id', models.CharField(max_length=15, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('iiq_id', models.UUIDField(blank=True, null=True)),
                ('fleid', models.CharField(blank=True, max_length=20, null=True)),
                ('type', models.CharField(choices=[('F', 'Staff'), ('S', 'Student'), ('N', 'None')], default='N', max_length=1)),
                ('name', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=30, unique=True)),
                ('is_remote', models.BooleanField(default=0)),
                ('status', models.BooleanField(default=0)),
                ('grade', models.CharField(blank=True, max_length=3, null=True)),
                ('remote', models.BooleanField(default=0)),
                ('password', models.CharField(blank=True, max_length=25, null=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('iiq_updated', models.DateTimeField(default=datetime.datetime(1800, 1, 1, 0, 0), verbose_name='IIQ Updated')),
                ('mosyle_updated', models.DateTimeField(default=datetime.datetime(1800, 1, 1, 0, 0), verbose_name='Mosyle Updated')),
                ('sadis_updated', models.DateTimeField(auto_now=True, verbose_name='SADIS Updated')),
                ('foreign_status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.studentstatuses')),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.location')),
                ('role', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.studentrole')),
            ],
            options={
                'verbose_name': 'Student',
                'verbose_name_plural': 'Students',
                'ordering': ['id', 'name'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalStudentModel',
            fields=[
                ('id', models.CharField(db_index=True, max_length=15, verbose_name='ID')),
                ('iiq_id', models.UUIDField(blank=True, null=True)),
                ('fleid', models.CharField(blank=True, max_length=20, null=True)),
                ('type', models.CharField(choices=[('F', 'Staff'), ('S', 'Student'), ('N', 'None')], default='N', max_length=1)),
                ('name', models.CharField(max_length=50)),
                ('username', models.CharField(db_index=True, max_length=30)),
                ('is_remote', models.BooleanField(default=0)),
                ('status', models.BooleanField(default=0)),
                ('grade', models.CharField(blank=True, max_length=3, null=True)),
                ('remote', models.BooleanField(default=0)),
                ('password', models.CharField(blank=True, max_length=25, null=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('iiq_updated', models.DateTimeField(default=datetime.datetime(1800, 1, 1, 0, 0), verbose_name='IIQ Updated')),
                ('mosyle_updated', models.DateTimeField(default=datetime.datetime(1800, 1, 1, 0, 0), verbose_name='Mosyle Updated')),
                ('sadis_updated', models.DateTimeField(blank=True, editable=False, verbose_name='SADIS Updated')),
                ('history_change_reason', models.TextField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('foreign_status', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='users.studentstatuses')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='inventory.location')),
                ('role', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='users.studentrole')),
            ],
            options={
                'verbose_name': 'historical Student',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
