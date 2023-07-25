# Django
from django.core.management.base import BaseCommand, CommandError
# SADIS
from inventory.models import Device, DeviceHistoryData
from inventory.utilities import is_not_blank

class Command(BaseCommand):
    help = 'Duplicate device history from old historical archive to new model archive.'

    def handle(self, *args, **options):
        devices = Device.objects.all()

        success_count = 0
        error_count = 0

        for device in devices:
            device_history = device.history.all()

            for record in device_history:
                try:
                    device_id = record.id
                    author_id = (record.history_user.id if record.history_user else "unknown")
                    author_username = (record.history_user.username if record.history_user else "unknown")
                    author_name = (record.history_user.get_full_name() if record.history_user else "Unknown")
                    assign_date = record.history_date

                    if record.owner:
                        owner_id = (record.owner.id if record.owner else "unknown")
                        owner_name = (record.owner.name if record.owner else "Unknown")
                        assign_type = 'Assigned'
                    else:
                        owner_id = (record.prev_record.owner.id if record.prev_record and record.prev_record.owner else "unknown")
                        owner_name = (record.prev_record.owner.name if record.prev_record and record.prev_record.owner else "Unknown")
                        assign_type = 'Unassigned'

                    DeviceHistoryData.objects.create(
                        device_id = device_id,
                        owner_id = owner_id,
                        owner_name = owner_name,
                        author_id = author_id,
                        author_username = author_username,
                        author_name = author_name,
                        assign_type = assign_type,
                        assign_date = assign_date
                    )

                    success_count += 1
                    print(f'{author_name} / {assign_type} / {owner_name} / {device_id} / {assign_date}')
                except:
                    error_count += 1

                    pass

        print('')
        print(f'Successful: {success_count} / Errored: {error_count}')
