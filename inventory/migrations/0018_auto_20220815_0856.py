# Generated by Django 3.2.13 on 2022-08-15 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_alter_device_owner_alter_historicaldevice_owner'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='charger',
            options={'verbose_name': 'Peripheral', 'verbose_name_plural': 'Peripherals'},
        ),
        migrations.AlterModelOptions(
            name='chargercondition',
            options={'verbose_name': 'Peripheral Condition', 'verbose_name_plural': 'Peripheral Conditions'},
        ),
        migrations.AlterModelOptions(
            name='chargertype',
            options={'verbose_name': 'Peripheral Type', 'verbose_name_plural': 'Peripheral Types'},
        ),
    ]
