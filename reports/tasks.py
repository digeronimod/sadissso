# Python
import csv, uuid
from datetime import datetime, date
# Django
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
# Plugins
from constance import config as constance_config
# Application
from inventory.models import Device
from sadis.celery import app as celery_app
from users.models import StudentModelIDLog, StudentModelPrograms, StudentModel, StudentChargerOwnership, StudentDeviceOwnership, DataDistribution, DataStaging

@celery_app.task
def celery_staging_data():
    staging_data = DataStaging.objects.filter(updated__gte = constance_config.dlmr_year_start, device_bpi__isnull = False)

    total_records = staging_data.count()
    completed_records = 0

    celery_staging_data.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Gathering...', 'filename': None})

    data = {}
    for record in staging_data:
        try:
            device = Device.objects.get(id = record.device_bpi)
        except:
            device = False

        if device != False:
            try:
                student = StudentModel.objects.get(id = record.student_id)

                if DataStaging.objects.filter(student_id = student.id).exists():
                    try:
                        sdata_history = DataStaging.history.filter(student_id = student.id).latest()
                        staging_author = sdata_history.history_user.get_full_name()
                    except:
                        staging_author = 'Unknown'

                data.update({
                    student.id: {
                        'student_id': student.id,
                        'student_name': student.name,
                        'device_id': record.device_bpi,
                        'device_model': device.foreign_model.name,
                        'device_bin': record.device_bin,
                        'stage_author': staging_author,
                        'stage_date': record.updated
                    }
                })
            except:
                pass

            completed_records += 1

            celery_staging_data.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Compiling...', 'filename': None})

    headers = ['student_id', 'student_name', 'device_id', 'device_model', 'device_bin', 'stage_author', 'stage_date']

    celery_staging_data.update_state(state = 'GENERATING', meta = {'current': completed_records, 'total': total_records, 'description': 'Generating CSV...', 'filename': None})

    filepath = f"{settings.MEDIA_ROOT}/reports/"
    filename = f"{str(uuid.uuid4())}.csv"

    with open(filepath + filename, "w+") as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for key in data:
            writer.writerow({field: data[key].get(field) or key for field in headers})

    response_data = {'current': completed_records, 'total': total_records, 'description': 'Downloading...', 'filename': filename, 'filepath': f'{settings.MEDIA_URL}reports/{filename}'}

    return response_data

@celery_app.task
def celery_student_devices():
    dlmr_year_start = constance_config.dlmr_year_start

    def get_distribution_data(student_id = None):
        if student_id != None:
            distribution_data = DataDistribution.objects.filter(student_id = student_id)

            if distribution_data.count() > 0:
                if distribution_data.last().updated.date() >= constance_config.dlmr_year_start:
                    return '23-24'
                elif date(2023, 5, 5) < distribution_data.last().updated.date() < constance_config.dlmr_year_start:
                    return '22-23'
                else:
                    return 'None'
            else:
                return 'None'
        else:
            return 'None'

    def get_staged_data(student_id = None):
        if student_id != None:
            staging_data = DataStaging.objects.filter(student_id = student_id, updated__gte = timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time())))

            if staging_data.count() > 0:
                return [staging_data.last().device_bin, staging_data.last().device_bpi]
            else:
                return 'None'
        else:
            return 'None'

    students = StudentModel.objects.all()

    total_records = students.count()
    completed_records = 0

    celery_student_devices.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Gathering...', 'filename': None})

    data = []
    for student in students:
        devices_owned = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id = student.id)
        staged_data = get_staged_data(student.id)

        data.append({
            'student_id': student.id,
            'student_first_name': student.name.split(' ', 1)[0],
            'student_last_name': student.name.split(' ', 1)[1],
            'student_location': (student.location.id if student.location else '0000'),
            'student_grade': (student.grade if student.grade else 'None'),
            'student_status': (student.status.id if student.status else 'None'),
            'student_ec': (student.role.id if student.role else 'None'),
            'form_completed': get_distribution_data(student.id),
            'staged_bin': (staged_data[0] if staged_data else 'None'),
            'staged_bpi': (staged_data[1] if staged_data else 'None'),
            'staged_device_info': Device.objects.get(id = staged_data[1]).foreign_model.name if Device.objects.filter(id = staged_data[1]).exists() else 'None',
            'devices_owned': ', '.join(device.device.id for device in devices_owned) or 'None',
            'devices_owned_device_info': ', '.join(device.device.foreign_model.name for device in devices_owned) or 'None',
        })

        completed_records += 1

        celery_student_devices.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Compiling...', 'filename': None})

    headers = ['student_id', None, 'student_first_name', 'student_last_name', None, 'student_location', 'student_grade', None, 'student_status', 'student_ec', None, 'form_completed', None, None, 'staged_bin', 'staged_bpi', 'staged_device_info', 'devices_owned', 'devices_owned_device_info']

    celery_student_devices.update_state(state = 'GENERATING', meta = {'current': completed_records, 'total': total_records, 'description': 'Generating CSV...', 'filename': None})

    filepath = f"{settings.MEDIA_ROOT}/reports/"
    filename = f"{str(uuid.uuid4())}.csv"

    with open(filepath + filename, "w+") as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for row in data:
            writer.writerow(row)

    response_data = {'current': completed_records, 'total': total_records, 'description': 'Downloading...', 'filename': filename, 'filepath': f'{settings.MEDIA_URL}reports/{filename}'}

    return response_data

@celery_app.task
def celery_student_devices_full():
    dlmr_year_start = constance_config.dlmr_year_start

    def get_distribution_data(student_id = None):
        if student_id != None:
            distribution_data = DataDistribution.objects.filter(student_id = student_id)

            if distribution_data.count() > 0:
                if distribution_data.last().updated.date() >= constance_config.dlmr_year_start:
                    return '23-24'
                elif date(2023, 5, 5) < distribution_data.last().updated.date() < constance_config.dlmr_year_start:
                    return '22-23'
                else:
                    return 'None'
            else:
                return 'None'
        else:
            return 'None'

    def get_staged_data(student_id = None):
        if student_id != None:
            staging_data = DataStaging.objects.filter(student_id = student_id, updated__gte = timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time())))

            if staging_data.count() > 0:
                return [staging_data.last().device_bin, staging_data.last().device_bpi]
            else:
                return 'None'
        else:
            return 'None'

    students = StudentModel.objects.all()

    total_records = students.count()
    completed_records = 0

    celery_student_devices_full.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Gathering...', 'filename': None})

    data = []
    for student in students:
        devices_owned = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id = student.id)
        staged_data = get_staged_data(student.id)

        data.append({
            'student_id': student.id,
            'student_first_name': student.name.split(' ', 1)[0],
            'student_last_name': student.name.split(' ', 1)[1],
            'student_location': (student.location.id if student.location else '0000'),
            'student_grade': (student.grade if student.grade else 'None'),
            'student_status': (student.status.id if student.status else 'None'),
            'student_ec': (student.role.id if student.role else 'None'),
            'form_completed': get_distribution_data(student.id),
            'staged_bin': (staged_data[0] if staged_data else 'None'),
            'staged_bpi': (staged_data[1] if staged_data else 'None'),
            'staged_device_info': Device.objects.get(id = staged_data[1]).foreign_model.name if Device.objects.filter(id = staged_data[1]).exists() else 'None',
            'devices_owned': ', '.join(device.device.id for device in devices_owned) or 'None',
            'devices_owned_device_info': ', '.join(device.device.foreign_model.name for device in devices_owned) or 'None',
            'student_password': (student.password if student.password else 'None'),
            'student_username': student.username,
            'student_grad_year': (student.graduation_date if student.graduation_date else 'None')
        })

        completed_records += 1

        celery_student_devices_full.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Compiling...', 'filename': None})

    headers = ['student_id', None, 'student_first_name', 'student_last_name', None, 'student_location', 'student_grade', None, 'student_status', 'student_ec', None, 'form_completed', None, None, 'staged_bin', 'staged_bpi', 'staged_device_info', 'devices_owned', 'devices_owned_device_info', 'student_password', 'student_username', 'student_grad_year']

    celery_student_devices_full.update_state(state = 'GENERATING', meta = {'current': completed_records, 'total': total_records, 'description': 'Generating CSV...', 'filename': None})

    filepath = f"{settings.MEDIA_ROOT}/reports/"
    filename = f"{str(uuid.uuid4())}.csv"

    with open(filepath + filename, "w+") as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for row in data:
            writer.writerow(row)

    response_data = {'current': completed_records, 'total': total_records, 'description': 'Downloading...', 'filename': filename, 'filepath': f'{settings.MEDIA_URL}reports/{filename}'}

    return response_data

@celery_app.task
def celery_student_enrollment():
    students = StudentModelPrograms.objects.all().select_related('student', 'student__location', 'program')

    total_records = students.count()
    completed_records = 0

    celery_student_enrollment.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Gathering...', 'filename': None})

    data = []
    for record in students:
        data.append({
            'fleid': record.student.unique_id if record.student.unique_id else 'N/A',
            'other_id': record.student.id,
            'grade': record.student.grade if record.student.grade else 'N/A',
            'first_name': record.student.name.split(' ')[0],
            'last_name': record.student.name.split(' ', 1)[1],
            'full_name': f"{record.student.name.split(' ', 1)[1]}, {record.student.name.split(' ')[0]}",
            'school': record.student.location.name if record.student.location else 'N/A',
            'status': record.student.status.id if record.student.status else 'N/A',
            'program': record.program.name,
            'program_start': record.program.begin.strftime('%m-%d-%Y'),
            'program_end': record.program.expiration.strftime('%m-%d-%Y'),
            'submitted_by': record.author.get_full_name()
        })

        completed_records += 1

        celery_student_enrollment.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Compiling...', 'filename': None})

    headers = ['fleid', 'other_id', 'grade', 'first_name', 'last_name', 'full_name', 'school', 'status', 'program', 'program_start', 'program_end', 'submitted_by']

    celery_student_enrollment.update_state(state = 'GENERATING', meta = {'current': completed_records, 'total': total_records, 'description': 'Generating CSV...', 'filename': None})

    filepath = f"{settings.MEDIA_ROOT}/reports/summer/"
    filename = f"{str(uuid.uuid4())}.csv"

    with open(filepath + filename, "w+") as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for row in data:
            writer.writerow(row)

    response_data = {'current': completed_records, 'total': total_records, 'description': 'Downloading...', 'filename': filename, 'filepath': f'{settings.MEDIA_URL}reports/summer/{filename}'}

    return response_data

@celery_app.task
def celery_temporary_ids():
    entries = StudentModelIDLog.objects.all().select_related('student', 'student__location', 'author')

    total_records = entries.count()
    completed_records = 0

    celery_temporary_ids.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Gathering...', 'filename': None})

    data = []
    for record in entries:
        data.append({
            'student_id': record.student.id,
            'student_username': record.student.username,
            'student_name': record.student.name,
            'grade': record.student.grade if record.student.grade else 'N/A',
            'school': record.student.location.name if record.student.location else 'N/A',
            'date_issued': record.date.strftime('%m-%d-%Y'),
            'printed_by': record.author.get_full_name()
        })

        completed_records += 1

        celery_temporary_ids.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Compiling...', 'filename': None})

    headers = ['student_id', 'student_username', 'student_name', 'grade', 'school', 'date_issued', 'printed_by']

    celery_temporary_ids.update_state(state = 'GENERATING', meta = {'current': completed_records, 'total': total_records, 'description': 'Generating CSV...', 'filename': None})

    filepath = f"{settings.MEDIA_ROOT}/reports/temporary_ids/"
    filename = f"{str(uuid.uuid4())}.csv"

    with open(filepath + filename, "w+") as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for row in data:
            writer.writerow(row)

    response_data = {'current': completed_records, 'total': total_records, 'description': 'Downloading...', 'filename': filename, 'filepath': f'{settings.MEDIA_URL}reports/temporary_ids/{filename}'}

    return response_data

@celery_app.task
def celery_case_assignments():
    entries = StudentModel.objects.all().select_related('location')

    total_records = entries.count()
    completed_records = 0

    celery_case_assignments.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Gathering...', 'filename': None})

    data = []
    for record in entries:
        data.append({
            'student_id': record.id,
            'student_username': record.username,
            'student_name': record.name,
            'grade': record.grade if record.grade else 'N/A',
            'school': record.location.name if record.location else 'N/A',
            'has_case': 'Yes' if StudentChargerOwnership.objects.filter(student = record, charger__type_id = '.5m1case').exists() else 'No'
        })

        completed_records += 1

        celery_case_assignments.update_state(state = 'INPROGRESS', meta = {'current': completed_records, 'total': total_records, 'description': 'Compiling...', 'filename': None})

    headers = ['student_id', 'student_username', 'student_name', 'grade', 'school', 'has_case']

    celery_case_assignments.update_state(state = 'GENERATING', meta = {'current': completed_records, 'total': total_records, 'description': 'Generating CSV...', 'filename': None})

    filepath = f"{settings.MEDIA_ROOT}/reports/case_assignments/"
    filename = f"{str(uuid.uuid4())}.csv"

    with open(filepath + filename, "w+") as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for row in data:
            writer.writerow(row)

    response_data = {'current': completed_records, 'total': total_records, 'description': 'Downloading...', 'filename': filename, 'filepath': f'{settings.MEDIA_URL}reports/case_assignments/{filename}'}

    return response_data
