# Python
import re
from datetime import datetime, date
# Django
from django.core.management.base import BaseCommand
from django.utils import timezone
# Plugins
from constance import config as constance_config
# SADIS
from inventory.models import Location, LocationCode
from sadis.api import api_edfi as edfi
from users.models import StudentModel

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
    help = 'Sync all students data from Ed-Fi'

    def handle(self, *args, **options):
        def request_students_data(offset):
            data = edfi.get_students_data(offset = offset)
            return data

        def request_additional_data(offset):
            data = edfi.get_students_additional_data(offset = offset)
            return data

        count_tracker = 0
        requested_data = request_students_data(offset = count_tracker)
        request_count = len(requested_data)

        while request_count > 0:
            for student in requested_data:
                other_id = None
                fle_id = None

                for id in student['identificationCodes']:
                    if 'Other ID' in id['studentIdentificationSystemDescriptor']:
                        other_id = id['identificationCode']

                    if 'FLEID' in id['studentIdentificationSystemDescriptor']:
                        fle_id = id['identificationCode']

                username = f'{normalize_string(student["firstName"])}{normalize_string(student["lastSurname"])[:3]}{other_id[-4:]}'

                for email in student['electronicMails']:
                    if '@flaglercps.org' in email['electronicMailAddress']:
                        local, at, domain = email['electronicMailAddress'].rpartition('@')
                        username = local.lower()

                name = f'{title_case(student["firstName"])} {title_case(student["lastSurname"])}'
                birthdate = datetime.strptime(student['birthDate'], '%Y-%m-%dT%H:%M:%S').date()

                if not StudentModel.objects.filter(unique_id = fle_id).exists():
                    print(f'Adding new student {name}...')

                    try:
                        new_student = StudentModel(
                            id = other_id,
                            unique_id = fle_id,
                            name = name,
                            username = username,
                            birthdate = birthdate,
                            status_id = 'N',
                            updated = timezone.now()
                        )

                        new_student.save_without_historical_record()
                    except:
                        print(f'Unable to add student {name}: Other ID is probably missing.')
                else:
                    updated_student = StudentModel.objects.get(unique_id = fle_id)

                    print(f'Updating student {updated_student.name}...')

                    if 'FL' in updated_student.id:
                        updated_student.id = other_id

                    updated_student.name = name
                    updated_student.username = username
                    updated_student.birthdate = birthdate
                    updated_student.updated = timezone.now()

                    if updated_student.status_id == 'N':
                        updated_student.status_id = 'A'

                    try:
                        updated_student.save_without_historical_record()
                    except:
                        pass

            count_tracker += request_count
            requested_data = request_students_data(offset = count_tracker)
            request_count = len(requested_data)

            if request_count == 0:
                break

        print(f'Finished querying {count_tracker} students!')

        count_tracker = 0
        requested_data = request_additional_data(offset = count_tracker)
        request_count = len(requested_data)

        while request_count > 0:
            for student in requested_data:
                fle_id = student['studentReference']['studentUniqueId']
                location_id = location_code = str(student['schoolReference']['schoolId'])[-4:]
                grade = student['entryGradeLevelDescriptor'][-2:]

                if StudentModel.objects.filter(unique_id = fle_id).exists():
                    updated_student = StudentModel.objects.get(unique_id = fle_id)

                    print(f'Updating additional information for {updated_student.name}...')

                    if location_code in LocationCode.objects.all().values_list('id', flat = True):
                        updated_student.location_code_id = location_code
                    else:
                        updated_student.location_code_id = 'UNK'

                    if location_id in ['3518', '3900', '9998']:
                        location_id = 'N998'
                    elif location_id == '9999':
                        location_id = '0091'

                    if location_id in Location.objects.all().values_list('id', flat = True):
                        updated_student.location_id = location_id
                    else:
                        updated_student.location_id = '0000'

                    # Temprorary patch for grade 31 report
                    if grade == '31':
                        if location_id in ['0022', '0051', '0061', '0131', '0201', '0301', '7004']:
                            grade = 'KG'

                    if grade in ['PK', 'KG', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', 'GD']:
                        updated_student.grade = grade
                    else:
                        updated_student.grade = None

                    if updated_student.status_id not in ['EYR', 'FLAG']:
                        if 'exitWithdrawDate' in student.keys():
                            updated_student.withdraw_date = datetime.strptime(student['exitWithdrawDate'], '%Y-%m-%dT%H:%M:%S').date()

                            if updated_student.grade == 'GD':
                                updated_student.status_id = 'G'
                            else:
                                updated_student.status_id = 'W'
                        else:
                            if updated_student.status_id != 'SP':
                                updated_student.status_id = 'A'

                    if updated_student.status_id not in ['EYR', 'FLAG']:
                        if updated_student.role_id not in ['DEL', 'DU', 'DU*', 'DUF', 'DUP']:
                            if updated_student.grade in ['PK', 'GD'] and updated_student.status_id != 'W':
                                updated_student.role_id = 'None'
                            elif updated_student.grade in ['KG', '01', '02', '03'] and updated_student.status_id != 'W':
                                updated_student.role_id = 'ICVL'
                            elif updated_student.grade in ['04', '05', '06', '07', '08', '09', '10', '11', '12'] and updated_student.status_id != 'W':
                                updated_student.role_id = 'OTO'
                            else:
                                updated_student.role_id = 'None'
                    else:
                        if updated_student.status_id == 'FLAG':
                            updated_student.role_id = 'None'

                    if 'graduationPlanReference' in student.keys():
                        updated_student.graduation_date = date(student['graduationPlanReference']['graduationSchoolYear'], 6, 1)

                    updated_student.save_without_historical_record()

            count_tracker += request_count
            requested_data = request_additional_data(offset = count_tracker)
            request_count = len(requested_data)

            if request_count == 0:
                break

        constance_config.sync_edfi = timezone.now()
        print(f'Finished adding information to {count_tracker} students!')
