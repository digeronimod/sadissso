# Python
import csv
# Django
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Plugins
from celery.result import AsyncResult
# SADIS
from .tasks import celery_staging_data, celery_student_devices, celery_student_devices_full, celery_student_enrollment, celery_temporary_ids, celery_case_assignments
from common.export import CSVStream
from inventory.models import Device
from inventory.utilities import is_not_blank
from users.decorators import allowed_users
from users.models import StudentModel, DataDistribution, DataStaging

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def export_csv(request):
    ...

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrator', 'Staff'])
def export(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'
    students = StudentModel.objects.all()

    data_headers = ['student_id', 'student_ec', 'student_status', 'form_completed', 'student_phone', 'staged_bin', 'staged_bpi', 'devices_owned']
    data_dictionary = {}

    for student in students:
        devices_owned = Device.objects.filter(Q(model__icontains = 'macbook') | Q(model__icontains = 'ipad'), owner_id = student.id)

        data_dictionary.update({
            student.id: {
                'student_ec': student.get_role_id(),
                'student_status': student.foreign_status.id if student.foreign_status else 'None',
                'form_completed': 'False',
                'student_phone': 'None',
                'staged_bin': 'None',
                'staged_bpi': 'None',
                'devices_owned': ', '.join(device.id for device in devices_owned) or 'None',
            }
        })

        if DataDistribution.objects.filter(student_id = student.id).exists():
            distribution_data = DataDistribution.objects.get(student_id = student.id)

            if is_not_blank(distribution_data.parent_phone):
                data_dictionary[student.id]['student_phone'] = distribution_data.parent_phone

            if int(distribution_data.updated.strftime('%Y')) >= 2020:
                data_dictionary[student.id]['form_completed'] = True

        if DataStaging.objects.filter(student_id = student.id).exists():
            staging_data = DataStaging.objects.get(student_id = student.id)

            if is_not_blank(staging_data.device_bpi):
                data_dictionary[student.id]['staged_bpi'] = staging_data.device_bpi

            if is_not_blank(staging_data.device_bin):
                data_dictionary[student.id]['staged_bin'] = staging_data.device_bin

    writer = csv.DictWriter(response, data_headers)
    writer.writeheader()

    for key in data_dictionary:
        writer.writerow({field: data_dictionary[key].get(field) or key for field in data_headers})

    return response

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrator', 'Staff'])
def export_distributions_signups(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_request.csv"'

    data_headers = ['student_id', 'student_name', 'form_completed', 'student_location', 'student_grade']
    data_dictionary = request.session.pop('requested_model')

    writer = csv.DictWriter(response, data_headers)
    writer.writeheader()

    for key in data_dictionary:
        writer.writerow({field: data_dictionary[key].get(field) or key for field in data_headers})

    return response

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrator', 'Staff'])
def export_distributions_devices(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_request.csv"'

    data_headers = ['device_id', 'device_model', 'student_id', 'student_name', 'form_completed', 'student_location', 'student_grade']
    data_dictionary = request.session.pop('requested_model')

    writer = csv.DictWriter(response, data_headers)
    writer.writeheader()

    for key in data_dictionary:
        writer.writerow({field: data_dictionary[key].get(field) or key for field in data_headers})

    return response

@csrf_exempt
def get_progress_state(request):
    if 'task_id' in request.session:
        task_id = request.session['task_id']
        task = AsyncResult(task_id)
        response_data = task.result
    else:
        JsonResponse({'message': 'No task ID was saved to your session or could be pulled from request.'})

    return JsonResponse(response_data, safe = False)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def export_staging_data(request):
    job = celery_staging_data.delay()
    request.session['task_id'] = job.id

    return JsonResponse({'task_id': job.id})

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def export_student_devices(request):
    job = celery_student_devices.delay()
    request.session['task_id'] = job.id

    return JsonResponse({'task_id': job.id})

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def export_student_enrollment(request):
    job = celery_student_enrollment.delay()
    request.session['task_id'] = job.id

    return JsonResponse({'task_id': job.id})

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def export_student_devices_full(request):
    job = celery_student_devices_full.delay()
    request.session['task_id'] = job.id

    return JsonResponse({'task_id': job.id})

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff', 'IDOnly'])
def export_temporary_ids(request):
    job = celery_temporary_ids.delay()
    request.session['task_id'] = job.id

    return JsonResponse({'task_id': job.id})

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def export_case_assignments(request):
    job = celery_case_assignments.delay()
    request.session['task_id'] = job.id

    return JsonResponse({'task_id': job.id})
