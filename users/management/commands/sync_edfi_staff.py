# Python
import re
from datetime import datetime
# Django
from django.core.management.base import BaseCommand
from django.utils import timezone
# SADIS
from sadis.api import api_edfi as edfi
from users.models import StaffModel

def title_case(string):
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), string)

def normalize_string(string):
    return re.sub('[^A-Za-z0-9]+', '', string).lower()

def is_integer(string):
    try:
        int(string)

        return True
    except ValueError:
        return False

class Command(BaseCommand):
    help = 'Sync all staffs data from Ed-Fi'

    def handle(self, *args, **options):
        def request_staffs_data(offset):
            data = edfi.get_staffs_data(offset = offset)
            return data

        def request_additional_data(offset):
            data = edfi.get_staffs_additional_data(offset = offset)
            return data

        count_tracker = 0
        requested_data = request_staffs_data(offset = count_tracker)
        request_count = len(requested_data)

        while request_count > 0:
            for staff in requested_data:
                local, at, domain = [None, None, None]
                other_id = None
                fle_id = None

                for email in staff['electronicMails']:
                    if email['electronicMailType'] == 'Work' and 'flaglerschools.com' in email['electronicMailAddress']:
                        local, at, domain = email['electronicMailAddress'].rpartition('@')

                if domain == 'flaglerschools.com':
                    for id in staff['identificationCodes']:
                        if 'Employee ID' in id['staffIdentificationSystemDescriptor']:
                            other_id = id['identificationCode']

                        if 'FLEID' in id['staffIdentificationSystemDescriptor']:
                            fle_id = id['identificationCode']

                    username = local.lower()
                    name = f'{title_case(staff["firstName"])} {title_case(staff["lastSurname"])}'
                    birthdate = datetime.strptime(staff['birthDate'], '%Y-%m-%dT%H:%M:%S').date()

                    if not StaffModel.objects.filter(unique_id = fle_id).exists():
                        print(f'Adding new staff {name}...')

                        try:
                            new_staff = StaffModel(
                                id = other_id,
                                unique_id = fle_id,
                                name = name,
                                username = username,
                                birthdate = birthdate,
                                updated = timezone.now()
                            )

                            new_staff.save_without_historical_record()
                        except:
                            print(f'Unable to add staff {name}: Other ID is probably missing.')
                    else:
                        updated_staff = StaffModel.objects.get(unique_id = fle_id)

                        print(f'Updating staff {updated_staff.name}...')

                        if 'FL' in updated_staff.id:
                            updated_staff.id = other_id

                        updated_staff.name = name
                        updated_staff.username = username
                        updated_staff.birthdate = birthdate
                        updated_staff.updated = timezone.now()

                        try:
                            updated_staff.save_without_historical_record()
                        except:
                            delete_queryset = StaffModel.objects.filter(unique_id = fle_id).delete()
                            updated_staff.save_without_historical_record()

            count_tracker += request_count
            requested_data = request_staffs_data(offset = count_tracker)
            request_count = len(requested_data)

            if request_count == 0:
                break

        print(f'Finished querying {count_tracker} staffs!')
