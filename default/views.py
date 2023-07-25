# Python
import json, markdown2
# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
# SADIS
from .models import Device, Note, PersonPrograms, CalendlyAppointment
from .utilities import get_query
from users.decorators import allowed_users
from users.models import Device, StudentDeviceOwnership, StudentModel, StudentModelPrograms

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff', 'Counselor', 'Viewer'])
def changelog(request):
    changelog = markdown2.markdown_path('CHANGELOG.md')

    context = {
        'changelog': changelog
    }

    return render(request, 'inventory/changelog.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff', 'Counselor', 'Viewer'])
def home(request):
    if 'IDOnly' in list(request.user.groups.values_list('name', flat = True)):
        id_only = True
    else:
        id_only = False

    users = StudentModel.objects.all()
    devices = Device.objects.all()

    owned_devices = StudentDeviceOwnership.objects.filter(student__isnull = False).count()

    total_user_count = users.count()
    active_user_count = users.filter(status_id__in = ['A', 'SP', 'EYR', 'IT', 'MC', 'N']).count()

    device_count = devices.count()
    unassigned_devices = devices.count() - owned_devices

    context = {
        'device_count': device_count,
        'unassigned_devices': unassigned_devices,
        'total_user_count': total_user_count,
        'active_user_count': active_user_count,
        'id_only': id_only
    }

    return render(request, 'inventory/index.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator'])
def scl(request):
    context = {}

    return render(request, 'inventory/scl.html', context)

@csrf_exempt
@require_POST
def calendly_appointment(request):
    status = 400
    data = json.loads(request.body)

    with open("request_data.json", "w") as datafile:
        datafile.write(json.dumps(data))
        status = 201

    CalendlyAppointment.objects.create(data = data)

    if status == 201:
        return JsonResponse({"status": "Success", "data": {"message": "Request processed"}}, status = 204)
    else:
        return JsonResponse({"status": "Fail", "data": {"message": "Bad request"}}, status = 400)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff', 'Counselor', 'Viewer'])
def summer_program(request):
    summer_programs = PersonPrograms.objects.all()

    context = {
        'summer_programs': summer_programs
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('action') == 'student-search':
            student_query = request.POST.get('student_search')
            student_search = get_query(student_query, ['id', 'name'])
            student_entries = StudentModel.objects.filter(student_search)

            for student in student_entries:
                response_data.update({
                    student.id: {
                        'id': student.id,
                        'text': f'{student.id}: {student.name}'
                    }
                })

            return JsonResponse(response_data)

        if request.POST.get('action') == 'student-summer-program':
            print(request.POST)

            student = StudentModel.objects.get(id = request.POST.get('student_id'))
            summer_program = PersonPrograms.objects.get(id = request.POST.get('program_id'))

            note_content = f"Summer program enrollment for {summer_program.id}. Enrolled by {request.user.first_name} {request.user.last_name}."
            response_data = {}

            try:
                object, created = StudentModelPrograms.objects.update_or_create(student = student, defaults = {'created': timezone.now(), 'author': request.user, 'program': summer_program})
                Note.objects.create(item_id = student.id, body = note_content, author = request.user)

                student.status_id = 'SP'
                student.save_without_historical_record()

                response_data['response_code'] = 200
            except:
                response_data['response_code'] = 404

            if response_data['response_code'] == 200:
                response_data['response_message'] = f"Successfully applied the program to {student.name}. You may now select another student to apply an extension for, if desired."
            elif response_data['response_code'] == 404:
                response_data['response_message'] = f"Something went wrong trying to apply the program to {student.name}. Please try again or contact your school's Technology Department to investigate the issue further."

            return JsonResponse(response_data)

    return render(request, 'inventory/summer_program.html', context)
