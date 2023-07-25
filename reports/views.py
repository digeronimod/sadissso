    # Python
import csv, json, uuid
from datetime import date, datetime, timedelta
from operator import itemgetter
# Django
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
# Plugins
from constance import config as constance_config
# SADIS
from inventory.models import PersonPrograms, CalendlyEvent, Device, DeviceModel, Location
from inventory.utilities import get_filters, get_query, make_ordinal, Qurl
from sadis import config
from users.decorators import allowed_users
from users.models import Student, StudentChargerOwnership, StudentModel, StudentDeviceOwnership, StudentModelIDLog, StudentModelPrograms, StudentAppointments, NewDataCollection, DataDistribution, DataStaging, L5QDistribution

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def export_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    headers = request.POST.get('headers').replace('[', '').replace(']', '').replace("'", '')
    dataset = json.loads(request.POST.get('dataset').replace('&quot;', '"'))

    data_fields = list(headers.split(', '))
    data_dictionary = {}

    for key, value in dataset.items():
        data_dictionary.update({
            key: value
        })

    writer = csv.DictWriter(response, data_fields)
    writer.writeheader()

    for key in data_dictionary:
        writer.writerow({field: data_dictionary[key].get(field) or key for field in data_fields})

    return response

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def home(request):
    if 'IDOnly' in list(request.user.groups.values_list('name', flat = True)):
        id_only = True
    else:
        id_only = False

    context = {
        'id_only': id_only
    }

    return render(request, 'reports/index.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def distributions_overview(request):
    if 'date' not in request.GET:
        return redirect(Qurl(request.build_absolute_uri()).add('date', f'{constance_config.dlmr_year_start.strftime("%m-%d-%Y")} - {date.today().strftime("%m-%d-%Y")}').get())

    if 'date' in request.GET:
        date_start = timezone.make_aware(datetime.combine(constance_config.dlmr_year_start, datetime.min.time()))
        date_today_min = timezone.make_aware(datetime.combine(date.today(), datetime.min.time()))
        date_today_max = timezone.make_aware(datetime.combine(date.today(), datetime.max.time()))
    else:
        date_start = timezone.make_aware(datetime.combine(constance_config.dlmr_year_start, datetime.min.time()))
        date_today_min = timezone.make_aware(datetime.combine(date.today(), datetime.min.time()))
        date_today_max = timezone.make_aware(datetime.combine(date.today(), datetime.max.time()))

    owned_devices = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__isnull = False, date__gte = date_start)
    distribution_data = DataDistribution.objects.filter(created__range = [date_start, date_today_max])

    context = {
        'distribution_data': distribution_data,
        'owned_devices': owned_devices,
        # FPCHS
        'fpc_registrations_total': distribution_data.filter(student_location_id = '0091'),
        'fpc_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0091'),
        'fpc_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0091'),
        'fpc_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0091'),
        # MHS
        'mhs_registrations_total': distribution_data.filter(student_location_id = '0090'),
        'mhs_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0090'),
        'mhs_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0090'),
        'mhs_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0090'),
        # BTMS
        'btms_registrations_total': distribution_data.filter(student_location_id = '0011'),
        'btms_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0011'),
        'btms_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0011'),
        'btms_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0011'),
        # ITMS
        'itms_registrations_total': distribution_data.filter(student_location_id = '0401'),
        'itms_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0401'),
        'itms_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0401'),
        'itms_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0401'),
        # BES
        'bes_registrations_total': distribution_data.filter(student_location_id = '0022'),
        'bes_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0022'),
        'bes_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0022'),
        'bes_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0022'),
        # BTES
        'btes_registrations_total': distribution_data.filter(student_location_id = '0301'),
        'btes_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0301'),
        'btes_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0301'),
        'btes_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0301'),
        # OKES
        'okes_registrations_total': distribution_data.filter(student_location_id = '0201'),
        'okes_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0201'),
        'okes_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0201'),
        'okes_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0201'),
        # RES
        'res_registrations_total': distribution_data.filter(student_location_id = '0051'),
        'res_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0051'),
        'res_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0051'),
        'res_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0051'),
        # WES
        'wes_registrations_total': distribution_data.filter(student_location_id = '0131'),
        'wes_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '0131'),
        'wes_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '0131'),
        'wes_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '0131'),
        # IF
        'if_registrations_total': distribution_data.filter(student_location_id = '7004'),
        'if_registrations_today': distribution_data.filter(created__range = [date_today_min, date_today_max], student_location_id = '7004'),
        'if_assignments_total': owned_devices.filter(date__range = [date_start, date_today_max], student__location_id = '7004'),
        'if_assignments_today': owned_devices.filter(date__range = [date_today_min, date_today_max], student__location_id = '7004')
    }

    if request.method == 'POST':
        if request.POST.get('action') == 'get-distribution-signups':
            requested_model = context[request.POST.get('model')]
            response_context = {
                "title": "District Signups",
                "title_tag": request.POST.get('model'),
                "students": {}
            }

            if requested_model:
                for entry in requested_model:
                    unique_uuid = uuid.uuid4()

                    dictionary = {
                        unique_uuid: {
                            "student_id": entry.student_id,
                            "student_name": f"{entry.student_first_name} {entry.student_last_name}",
                            "form_completed": "N/A",
                            "student_location": entry.student_location_id,
                            "student_grade": make_ordinal(entry.student_grade)
                        }
                    }

                    if entry.created.date() >= constance_config.dlmr_year_start:
                        dictionary[unique_uuid]['form_completed'] = '23-24'
                    elif date(2022, 5, 8) <= entry.created.date() <= constance_config.dlmr_year_start:
                        dictionary[unique_uuid]['form_completed'] = '22-23'

                    response_context['students'].update(dictionary)

                request.session['requested_model'] = response_context['students']
                html = render_to_string('reports/distributions_signups_modal.html', response_context, request)

                return HttpResponse(html)
            else:
                return HttpResponse("Requested model does not exist in the context entries.")
        elif request.POST.get('action') == 'get-distribution-devices':
            requested_model = context[request.POST.get('model')]
            response_context = {
                "title": "District Owned Devices",
                "title_tag": request.POST.get('model'),
                "students": {}
            }

            if requested_model:
                for entry in requested_model:
                    form_exists = DataDistribution.objects.filter(student_id = entry.student.id).exists()

                    if form_exists:
                        form_object = DataDistribution.objects.get(student_id = entry.student.id)

                        if form_object.created.date() >= date(2023, 5, 5):
                            form_date = '23-24'
                        elif form_object.created.date() < date(2023, 5, 5):
                            form_date = '22-23'
                        else:
                            form_date = 'N/A'
                    else:
                        form_date = 'None'

                    dictionary = {
                        str(uuid.uuid4()): {
                            "device_id": entry.device.id,
                            "device_model": entry.device.foreign_model.name,
                            "student_id": entry.student.id,
                            "student_name": entry.student.name,
                            "form_completed": form_date,
                            "student_location": entry.student.location.id,
                            "student_grade": make_ordinal(entry.student.grade)
                        }
                    }

                    response_context['students'].update(dictionary)

                request.session['requested_model'] = response_context['students']
                html = render_to_string('reports/distributions_devices_modal.html', response_context, request)

                return HttpResponse(html)
            else:
                return HttpResponse("Requested model does not exist in the context entries.")

    return render(request, 'reports/distributions_overview.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def distributions_calendly(request):
    def get_staged_data(student_id = None):
        if student_id != None:
            staging_data = DataStaging.objects.filter(student_id = student_id, updated__gte = timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time())))

            if staging_data.count() > 0:
                return [staging_data.last().device_bin, staging_data.last().device_bpi]
            else:
                return False
        else:
            return False

    page = request.GET.get('page', 1)
    url = request.get_full_path()
    current_datetime = timezone.now()

    locations = Location.objects.exclude(id__in = ['0061', '7005', '7006', '8000', '8001', '9999']).order_by('name')
    grades = config.CALENDLY_GRADE_LEVELS
    grade_levels = {'KG-03': {'display': 'KG-3rd', 'filter': ['KG', '03']}, '04-05': {'display': '4th-5th', 'filter': ['04', '05']}, '06-08': {'display': '6th-8th', 'filter': ['06', '08']}, '09-12': {'display': '9th-12th', 'filter': ['09', '12']}}
    yes_no = ['Yes', 'No']

    events = CalendlyEvent.objects.all()

    event_data = {}
    for event in events:
        event_data.update({
            event.event_id: {
                'event_name': event.event_name,
                'event_start': event.event_start,
                'event_end': event.event_end
            }
        })

    dlmr_year_start = constance_config.dlmr_year_start

    if 'has_device' in request.GET and request.GET['has_device'] == 'Yes':
        students = StudentAppointments.objects.filter(student__id__in = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad')).values_list('student_id', flat = True))
    elif 'has_device' in request.GET and request.GET['has_device'] == 'No':
        students = StudentAppointments.objects.exclude(student__id__in = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__isnull = False).values_list('student_id', flat = True))
    else:
        students = StudentAppointments.objects.all()

    if 'view_date' in request.GET:
        date_string = request.GET['view_date']
        date_object = datetime.strptime(date_string, '%m/%d/%Y')
        dated_students = students.filter(event__event_start__range = [date_object, date_object + timedelta(hours = 23, minutes = 59)])
        students = dated_students

    if 'grade' in request.GET:
        graded_students = students.filter(student__grade = request.GET['grade'])
        students = graded_students

    if 'grade_level' in request.GET:
        grade_filter = request.GET['grade_level']

        leveled_students = students.filter(student__grade__range = (grade_levels[grade_filter]['filter'][0], grade_levels[grade_filter]['filter'][1]))
        students = leveled_students

    if 'location' in request.GET:
        located_students = students.filter(student__location_id = request.GET['location'])
        students = located_students

    if 'is_staged' in request.GET and request.GET['is_staged'] == 'Yes':
        staged_students = students.filter(student__id__in = DataStaging.objects.filter(updated__gte = timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time()))).values_list('student_id', flat = True))
        students = staged_students
    elif 'is_staged' in request.GET and request.GET['is_staged'] == 'No':
        unstaged_students = students.exclude(student__id__in = DataStaging.objects.filter(updated__gte = timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time()))).values_list('student_id', flat = True))
        students = unstaged_students

    entries = students.order_by('id')
    total_entries = entries.count()

    paginator = Paginator(entries, 200)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    data_dates = []
    for event in CalendlyEvent.objects.all():
        current_datetime = datetime.strptime(date.today().strftime('%m/%d/%Y'), '%m/%d/%Y')

        if (event.event_start).strftime("%m/%d/%Y") not in data_dates:
            data_dates.append((event.event_start).strftime("%m/%d/%Y"))

    data_dates = sorted(data_dates)

    data_dictionary = {}
    for student in entries:
        devices_owned = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id = student.student.id)
        staged_data = get_staged_data(student.student.id)

        data_dictionary.update({
            student.student.id: {
                'student_id': student.student.id,
                'student_name': student.student.name,
                'student_username': student.student.username,
                'student_grade': student.student.grade,
                'student_location_id': student.student.location.id if student.student.location else None,
                'student_location_alias': student.student.location.alias if student.student.location else None,
                'student_location_name': student.student.location.name if student.student.location else None,
                'student_ec': student.student.role.name,
                'devices_owned': ', '.join(device.device.id for device in devices_owned) or None,
                'device_bin': staged_data[0] if staged_data else None,
                'device_bpi': staged_data[1] if staged_data else None,
                'appointment_time': student.event.event_start
            }
        })

    data_dictionary = sorted(data_dictionary.values(), key = itemgetter('appointment_time'))

    context = {
        # QuerySets
        'locations': locations,
        # Data
        'data_dictionary': data_dictionary,
        'data_dates': data_dates,
        # Variables
        'grades': grades,
        'grade_levels': grade_levels,
        'yes_no': yes_no,
        'total_entries': total_entries,
        # Search
        'entries': entries
    }

    return render(request, 'reports/distributions_calendly.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def collections_overview(request):
    view_date = date.today()
    dlmr_year_start = constance_config.dlmr_year_start

    if 'date' in request.GET:
        datetime_string = f'{request.GET.get("date")} 00:00:00'
        datetime_object = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')

        current_date = datetime_object
    else:
        current_date = datetime.combine(view_date, datetime.min.time())

    current_date_end = current_date + timedelta(hours = 23, minutes = 59)
    all_devices = StudentDeviceOwnership.objects.filter(Q(date__lt = dlmr_year_start) | Q(date__isnull = True))
    active_statuses = ['A', 'EYR', 'IT', 'MC', 'N', 'SP']
    inactive_statuses = ['FLAG', 'G', 'IA', 'W']

    # Matanzas High School
    mhs_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0090')
    mhs_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0090')
    mhs_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0090')

    mhs_12_active = mhs_active_students.filter(grade = '12')
    mhs_12_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = mhs_12_active.values_list('id', flat = True).distinct())
    mhs_12_collected = NewDataCollection.objects.filter(student__grade = '12', student__location_id = '0090', updated__gt = dlmr_year_start)
    mhs_11_active = mhs_active_students.filter(grade = '11')
    mhs_11_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = mhs_11_active.values_list('id', flat = True).distinct())
    mhs_11_collected = NewDataCollection.objects.filter(student__grade = '11', student__location_id = '0090', updated__gt = dlmr_year_start)
    mhs_10_active = mhs_active_students.filter(grade = '10')
    mhs_10_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = mhs_10_active.values_list('id', flat = True).distinct())
    mhs_10_collected = NewDataCollection.objects.filter(student__grade = '10', student__location_id = '0090', updated__gt = dlmr_year_start)
    mhs_09_active = mhs_active_students.filter(grade = '09')
    mhs_09_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = mhs_09_active.values_list('id', flat = True).distinct())
    mhs_09_collected = NewDataCollection.objects.filter(student__grade = '10', student__location_id = '0090', updated__gt = dlmr_year_start)

    # Flagler Palm Coast High School
    fpc_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0091')
    fpc_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0091')
    fpc_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0091')

    fpc_12_active = fpc_active_students.filter(grade = '12')
    fpc_12_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = fpc_12_active.values_list('id', flat = True).distinct())
    fpc_12_collected = NewDataCollection.objects.filter(student__grade = '12', student__location_id = '0091', updated__gt = dlmr_year_start)
    fpc_11_active = fpc_active_students.filter(grade = '11')
    fpc_11_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = fpc_11_active.values_list('id', flat = True).distinct())
    fpc_11_collected = NewDataCollection.objects.filter(student__grade = '11', student__location_id = '0091', updated__gt = dlmr_year_start)
    fpc_10_active = fpc_active_students.filter(grade = '10')
    fpc_10_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = fpc_10_active.values_list('id', flat = True).distinct())
    fpc_10_collected = NewDataCollection.objects.filter(student__grade = '10', student__location_id = '0091', updated__gt = dlmr_year_start)
    fpc_09_active = fpc_active_students.filter(grade = '09')
    fpc_09_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = fpc_09_active.values_list('id', flat = True).distinct())
    fpc_09_collected = NewDataCollection.objects.filter(student__grade = '09', student__location_id = '0091', updated__gt = dlmr_year_start)

    # Buddy Taylor Middle School
    btms_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0011')
    #btms_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0011')
    btms_active_wdevice = StudentDeviceOwnership.objects.filter(student__status_id__in = active_statuses, student__location_id = '0011')
    btms_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0011')
    
    btms_08_active = btms_active_students.filter(grade = '08')
    btms_08_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btms_08_active.values_list('id', flat = True).distinct())
    btms_08_collected = NewDataCollection.objects.filter(student__grade = '08', student__location_id = '0011', updated__gt = dlmr_year_start)
    btms_07_active = btms_active_students.filter(grade = '07')
    btms_07_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btms_07_active.values_list('id', flat = True).distinct())
    btms_07_collected = NewDataCollection.objects.filter(student__grade = '07', student__location_id = '0011', updated__gt = dlmr_year_start)
    btms_06_active = btms_active_students.filter(grade = '06')
    btms_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btms_06_active.values_list('id', flat = True).distinct())
    btms_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '0011', updated__gt = dlmr_year_start)

    # Indian Trails Middle School
    itms_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0401')
    itms_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0401')
    itms_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0401')

    itms_08_active = itms_active_students.filter(grade = '08')
    itms_08_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = itms_08_active.values_list('id', flat = True).distinct())
    itms_08_collected = NewDataCollection.objects.filter(student__grade = '08', student__location_id = '0401', updated__gt = dlmr_year_start)
    itms_07_active = itms_active_students.filter(grade = '07')
    itms_07_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = itms_07_active.values_list('id', flat = True).distinct())
    itms_07_collected = NewDataCollection.objects.filter(student__grade = '07', student__location_id = '0401', updated__gt = dlmr_year_start)
    itms_06_active = itms_active_students.filter(grade = '06')
    itms_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = itms_06_active.values_list('id', flat = True).distinct())
    itms_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '0401', updated__gt = dlmr_year_start)

    # Bunnell Elementary School
    bes_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0022')
    bes_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0022')
    bes_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0022')

    # bes_06_active = bes_active_students.filter(grade = '06')
    # bes_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = bes_06_active.values_list('id', flat = True).distinct())
    # bes_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '0022', updated__gt = dlmr_year_start)
    bes_05_active = bes_active_students.filter(grade = '05')
    bes_05_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = bes_05_active.values_list('id', flat = True).distinct())
    bes_05_collected = NewDataCollection.objects.filter(student__grade = '05', student__location_id = '0022', updated__gt = dlmr_year_start)
    bes_04_active = bes_active_students.filter(grade = '04')
    bes_04_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = bes_04_active.values_list('id', flat = True).distinct())
    bes_04_collected = NewDataCollection.objects.filter(student__grade = '04', student__location_id = '0022', updated__gt = dlmr_year_start)
    bes_03_active = bes_active_students.filter(grade = '03')
    bes_03_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = bes_03_active.values_list('id', flat = True).distinct())
    bes_03_collected = NewDataCollection.objects.filter(student__grade = '03', student__location_id = '0022', updated__gt = dlmr_year_start)
    bes_02_active = bes_active_students.filter(grade = '02')
    bes_02_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = bes_02_active.values_list('id', flat = True).distinct())
    bes_02_collected = NewDataCollection.objects.filter(student__grade = '02', student__location_id = '0022', updated__gt = dlmr_year_start)
    bes_01_active = bes_active_students.filter(grade = '01')
    bes_01_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = bes_01_active.values_list('id', flat = True).distinct())
    bes_01_collected = NewDataCollection.objects.filter(student__grade = '01', student__location_id = '0022', updated__gt = dlmr_year_start)
    bes_kg_active = bes_active_students.filter(grade = 'KG')
    bes_kg_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = bes_kg_active.values_list('id', flat = True).distinct())
    bes_kg_collected = NewDataCollection.objects.filter(student__grade = 'KG', student__location_id = '0022', updated__gt = dlmr_year_start)


    # Rymfire Elementary School
    res_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0051')
    res_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0051')
    res_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0051')

    # res_06_active = res_active_students.filter(grade = '06')
    # res_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = res_06_active.values_list('id', flat = True).distinct())
    # res_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '0051', updated__gt = dlmr_year_start)
    res_05_active = res_active_students.filter(grade = '05')
    res_05_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = res_05_active.values_list('id', flat = True).distinct())
    res_05_collected = NewDataCollection.objects.filter(student__grade = '05', student__location_id = '0051', updated__gt = dlmr_year_start)
    res_04_active = res_active_students.filter(grade = '04')
    res_04_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = res_04_active.values_list('id', flat = True).distinct())
    res_04_collected = NewDataCollection.objects.filter(student__grade = '04', student__location_id = '0051', updated__gt = dlmr_year_start)
    res_03_active = res_active_students.filter(grade = '03')
    res_03_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = res_03_active.values_list('id', flat = True).distinct())
    res_03_collected = NewDataCollection.objects.filter(student__grade = '03', student__location_id = '0051', updated__gt = dlmr_year_start)
    res_02_active = res_active_students.filter(grade = '02')
    res_02_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = res_02_active.values_list('id', flat = True).distinct())
    res_02_collected = NewDataCollection.objects.filter(student__grade = '02', student__location_id = '0051', updated__gt = dlmr_year_start)
    res_01_active = res_active_students.filter(grade = '01')
    res_01_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = res_01_active.values_list('id', flat = True).distinct())
    res_01_collected = NewDataCollection.objects.filter(student__grade = '01', student__location_id = '0051', updated__gt = dlmr_year_start)
    res_kg_active = res_active_students.filter(grade = 'KG')
    res_kg_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = res_kg_active.values_list('id', flat = True).distinct())
    res_kg_collected = NewDataCollection.objects.filter(student__grade = 'KG', student__location_id = '0051', updated__gt = dlmr_year_start)

    # Wadsworth Elementary School
    wes_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0131')
    wes_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0131')
    wes_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0131')

    # wes_06_active = wes_active_students.filter(grade = '06')
    # wes_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = wes_06_active.values_list('id', flat = True).distinct())
    # wes_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '0131', updated__gt = dlmr_year_start)
    wes_05_active = wes_active_students.filter(grade = '05')
    wes_05_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = wes_05_active.values_list('id', flat = True).distinct())
    wes_05_collected = NewDataCollection.objects.filter(student__grade = '05', student__location_id = '0131', updated__gt = dlmr_year_start)
    wes_04_active = wes_active_students.filter(grade = '04')
    wes_04_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = wes_04_active.values_list('id', flat = True).distinct())
    wes_04_collected = NewDataCollection.objects.filter(student__grade = '04', student__location_id = '0131', updated__gt = dlmr_year_start)
    wes_03_active = wes_active_students.filter(grade = '03')
    wes_03_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = wes_03_active.values_list('id', flat = True).distinct())
    wes_03_collected = NewDataCollection.objects.filter(student__grade = '03', student__location_id = '0131', updated__gt = dlmr_year_start)
    wes_02_active = wes_active_students.filter(grade = '02')
    wes_02_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = wes_02_active.values_list('id', flat = True).distinct())
    wes_02_collected = NewDataCollection.objects.filter(student__grade = '02', student__location_id = '0131', updated__gt = dlmr_year_start)
    wes_01_active = wes_active_students.filter(grade = '01')
    wes_01_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = wes_01_active.values_list('id', flat = True).distinct())
    wes_01_collected = NewDataCollection.objects.filter(student__grade = '01', student__location_id = '0131', updated__gt = dlmr_year_start)
    wes_kg_active = wes_active_students.filter(grade = 'KG')
    wes_kg_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = wes_kg_active.values_list('id', flat = True).distinct())
    wes_kg_collected = NewDataCollection.objects.filter(student__grade = 'KG', student__location_id = '0131', updated__gt = dlmr_year_start)

    # Old Kings Elementary School
    okes_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0201')
    okes_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0201')
    okes_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0201')

    # okes_06_active = okes_active_students.filter(grade = '06')
    # okes_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = okes_06_active.values_list('id', flat = True).distinct())
    # okes_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '0201', updated__gt = dlmr_year_start)
    okes_05_active = okes_active_students.filter(grade = '05')
    okes_05_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = okes_05_active.values_list('id', flat = True).distinct())
    okes_05_collected = NewDataCollection.objects.filter(student__grade = '05', student__location_id = '0201', updated__gt = dlmr_year_start)
    okes_04_active = okes_active_students.filter(grade = '04')
    okes_04_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = okes_04_active.values_list('id', flat = True).distinct())
    okes_04_collected = NewDataCollection.objects.filter(student__grade = '04', student__location_id = '0201', updated__gt = dlmr_year_start)
    okes_03_active = okes_active_students.filter(grade = '03')
    okes_03_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = okes_03_active.values_list('id', flat = True).distinct())
    okes_03_collected = NewDataCollection.objects.filter(student__grade = '03', student__location_id = '0201', updated__gt = dlmr_year_start)
    okes_02_active = okes_active_students.filter(grade = '02')
    okes_02_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = okes_02_active.values_list('id', flat = True).distinct())
    okes_02_collected = NewDataCollection.objects.filter(student__grade = '02', student__location_id = '0201', updated__gt = dlmr_year_start)
    okes_01_active = okes_active_students.filter(grade = '01')
    okes_01_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = okes_01_active.values_list('id', flat = True).distinct())
    okes_01_collected = NewDataCollection.objects.filter(student__grade = '01', student__location_id = '0201', updated__gt = dlmr_year_start)
    okes_kg_active = okes_active_students.filter(grade = 'KG')
    okes_kg_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = okes_kg_active.values_list('id', flat = True).distinct())
    okes_kg_collected = NewDataCollection.objects.filter(student__grade = 'KG', student__location_id = '0201', updated__gt = dlmr_year_start)

    # Belle Terre Elementary School
    btes_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '0301')
    btes_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '0301')
    btes_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '0301')

    # btes_06_active = btes_active_students.filter(grade = '06')
    # btes_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btes_06_active.values_list('id', flat = True).distinct())
    # btes_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '0301', updated__gt = dlmr_year_start)
    btes_05_active = btes_active_students.filter(grade = '05')
    btes_05_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btes_05_active.values_list('id', flat = True).distinct())
    btes_05_collected = NewDataCollection.objects.filter(student__grade = '05', student__location_id = '0301', updated__gt = dlmr_year_start)
    btes_04_active = btes_active_students.filter(grade = '04')
    btes_04_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btes_04_active.values_list('id', flat = True).distinct())
    btes_04_collected = NewDataCollection.objects.filter(student__grade = '04', student__location_id = '0301', updated__gt = dlmr_year_start)
    btes_03_active = btes_active_students.filter(grade = '03')
    btes_03_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btes_03_active.values_list('id', flat = True).distinct())
    btes_03_collected = NewDataCollection.objects.filter(student__grade = '03', student__location_id = '0301', updated__gt = dlmr_year_start)
    btes_02_active = btes_active_students.filter(grade = '02')
    btes_02_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btes_02_active.values_list('id', flat = True).distinct())
    btes_02_collected = NewDataCollection.objects.filter(student__grade = '02', student__location_id = '0301', updated__gt = dlmr_year_start)
    btes_01_active = btes_active_students.filter(grade = '01')
    btes_01_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btes_01_active.values_list('id', flat = True).distinct())
    btes_01_collected = NewDataCollection.objects.filter(student__grade = '01', student__location_id = '0301', updated__gt = dlmr_year_start)
    btes_kg_active = btes_active_students.filter(grade = 'KG')
    btes_kg_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = btes_kg_active.values_list('id', flat = True).distinct())
    btes_kg_collected = NewDataCollection.objects.filter(student__grade = 'KG', student__location_id = '0301', updated__gt = dlmr_year_start)

    # iFlagler
    if_active_students = StudentModel.objects.filter(status_id__in = active_statuses, location_id = '7004')
    if_active_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = active_statuses, student__location_id = '7004')
    if_inactive_wdevice = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student__status_id__in = inactive_statuses, student__location_id = '7004')

    if_12_active = if_active_students.filter(grade = '12')
    if_12_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_12_active.values_list('id', flat = True).distinct())
    if_12_collected = NewDataCollection.objects.filter(student__grade = '12', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_11_active = if_active_students.filter(grade = '11')
    if_11_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_11_active.values_list('id', flat = True).distinct())
    if_11_collected = NewDataCollection.objects.filter(student__grade = '11', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_10_active = if_active_students.filter(grade = '10')
    if_10_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_10_active.values_list('id', flat = True).distinct())
    if_10_collected = NewDataCollection.objects.filter(student__grade = '10', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_09_active = if_active_students.filter(grade = '09')
    if_09_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_09_active.values_list('id', flat = True).distinct())
    if_09_collected = NewDataCollection.objects.filter(student__grade = '10', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_08_active = if_active_students.filter(grade = '08')
    if_08_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_08_active.values_list('id', flat = True).distinct())
    if_08_collected = NewDataCollection.objects.filter(student__grade = '08', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_07_active = if_active_students.filter(grade = '07')
    if_07_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_07_active.values_list('id', flat = True).distinct())
    if_07_collected = NewDataCollection.objects.filter(student__grade = '07', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_06_active = if_active_students.filter(grade = '06')
    if_06_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_06_active.values_list('id', flat = True).distinct())
    if_06_collected = NewDataCollection.objects.filter(student__grade = '06', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_05_active = if_active_students.filter(grade = '05')
    if_05_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_05_active.values_list('id', flat = True).distinct())
    if_05_collected = NewDataCollection.objects.filter(student__grade = '05', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_04_active = if_active_students.filter(grade = '04')
    if_04_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_04_active.values_list('id', flat = True).distinct())
    if_04_collected = NewDataCollection.objects.filter(student__grade = '04', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_03_active = if_active_students.filter(grade = '03')
    if_03_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_03_active.values_list('id', flat = True).distinct())
    if_03_collected = NewDataCollection.objects.filter(student__grade = '03', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_02_active = if_active_students.filter(grade = '02')
    if_02_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_02_active.values_list('id', flat = True).distinct())
    if_02_collected = NewDataCollection.objects.filter(student__grade = '02', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_01_active = if_active_students.filter(grade = '01')
    if_01_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_01_active.values_list('id', flat = True).distinct())
    if_01_collected = NewDataCollection.objects.filter(student__grade = '01', student__location_id = '7004', updated__gt = dlmr_year_start)
    if_kg_active = if_active_students.filter(grade = 'KG')
    if_kg_wdevices = all_devices.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id__in = if_kg_active.values_list('id', flat = True).distinct())
    if_kg_collected = NewDataCollection.objects.filter(student__grade = 'KG', student__location_id = '7004', updated__gt = dlmr_year_start)

    context = {
        # Variables
        'current_date': current_date,
        'current_date_end': current_date_end,
        # Data: MHS
        'mhs_active_students': mhs_active_students,
        'mhs_active_wdevices': mhs_active_wdevice,
        'mhs_inactive_students': mhs_inactive_wdevice,
        'mhs_12_active': mhs_12_active,
        'mhs_12_wdevices': mhs_12_wdevices,
        'mhs_12_collected': mhs_12_collected,
        'mhs_11_active': mhs_11_active,
        'mhs_11_wdevices': mhs_11_wdevices,
        'mhs_11_collected': mhs_11_collected,
        'mhs_10_active': mhs_10_active,
        'mhs_10_wdevices': mhs_10_wdevices,
        'mhs_10_collected': mhs_10_collected,
        'mhs_09_active': mhs_09_active,
        'mhs_09_wdevices': mhs_09_wdevices,
        'mhs_09_collected': mhs_09_collected,
        # Data: FPCHS
        'fpc_active_students': fpc_active_students,
        'fpc_active_wdevices': fpc_active_wdevice,
        'fpc_inactive_students': fpc_inactive_wdevice,
        'fpc_12_active': fpc_12_active,
        'fpc_12_wdevices': fpc_12_wdevices,
        'fpc_12_collected': fpc_12_collected,
        'fpc_11_active': fpc_11_active,
        'fpc_11_wdevices': fpc_11_wdevices,
        'fpc_11_collected': fpc_11_collected,
        'fpc_10_active': fpc_10_active,
        'fpc_10_wdevices': fpc_10_wdevices,
        'fpc_10_collected': fpc_10_collected,
        'fpc_09_active': fpc_09_active,
        'fpc_09_wdevices': fpc_09_wdevices,
        'fpc_09_collected': fpc_09_collected,
        # Data: BTMS
        'btms_active_students': btms_active_students,
        'btms_active_wdevices': btms_active_wdevice,
        'btms_inactive_students': btms_inactive_wdevice,
        'btms_08_active': btms_08_active,
        'btms_08_wdevices': btms_08_wdevices,
        'btms_08_collected': btms_08_collected,
        'btms_07_active': btms_07_active,
        'btms_07_wdevices': btms_07_wdevices,
        'btms_07_collected': btms_07_collected,
        'btms_06_active': btms_06_active,
        'btms_06_wdevices': btms_06_wdevices,
        'btms_06_collected': btms_06_collected,
        # Data: ITMS
        'itms_active_students': itms_active_students,
        'itms_active_wdevices': itms_active_wdevice,
        'itms_inactive_students': itms_inactive_wdevice,
        'itms_08_active': itms_08_active,
        'itms_08_wdevices': itms_08_wdevices,
        'itms_08_collected': itms_08_collected,
        'itms_07_active': itms_07_active,
        'itms_07_wdevices': itms_07_wdevices,
        'itms_07_collected': itms_07_collected,
        'itms_06_active': itms_06_active,
        'itms_06_wdevices': itms_06_wdevices,
        'itms_06_collected': itms_06_collected,
        # Data: BES
        'bes_active_students': bes_active_students,
        'bes_active_wdevices': bes_active_wdevice,
        'bes_inactive_students': bes_inactive_wdevice,
        'bes_05_active': bes_05_active,
        'bes_05_wdevices': bes_05_wdevices,
        'bes_05_collected': bes_05_collected,
        'bes_04_active': bes_04_active,
        'bes_04_wdevices': bes_04_wdevices,
        'bes_04_collected': bes_04_collected,
        'bes_03_active': bes_03_active,
        'bes_03_wdevices': bes_03_wdevices,
        'bes_03_collected': bes_03_collected,
        'bes_02_active': bes_02_active,
        'bes_02_wdevices': bes_02_wdevices,
        'bes_02_collected': bes_02_collected,
        'bes_01_active': bes_01_active,
        'bes_01_wdevices': bes_01_wdevices,
        'bes_01_collected': bes_01_collected,
        'bes_kg_active': bes_kg_active,
        'bes_kg_wdevices': bes_kg_wdevices,
        'bes_kg_collected': bes_kg_collected,
        # Data: RES
        'res_active_students': res_active_students,
        'res_active_wdevices': res_active_wdevice,
        'res_inactive_students': res_inactive_wdevice,
        'res_05_active': res_05_active,
        'res_05_wdevices': res_05_wdevices,
        'res_05_collected': res_05_collected,
        'res_04_active': res_04_active,
        'res_04_wdevices': res_04_wdevices,
        'res_04_collected': res_04_collected,
        'res_03_active': res_03_active,
        'res_03_wdevices': res_03_wdevices,
        'res_03_collected': res_03_collected,
        'res_02_active': res_02_active,
        'res_02_wdevices': res_02_wdevices,
        'res_02_collected': res_02_collected,
        'res_01_active': res_01_active,
        'res_01_wdevices': res_01_wdevices,
        'res_01_collected': res_01_collected,
        'res_kg_active': res_kg_active,
        'res_kg_wdevices': res_kg_wdevices,
        'res_kg_collected': res_kg_collected,
        # Data: WES
        'wes_active_students': wes_active_students,
        'wes_active_wdevices': wes_active_wdevice,
        'wes_inactive_students': wes_inactive_wdevice,
        'wes_05_active': wes_05_active,
        'wes_05_wdevices': wes_05_wdevices,
        'wes_05_collected': wes_05_collected,
        'wes_04_active': wes_04_active,
        'wes_04_wdevices': wes_04_wdevices,
        'wes_04_collected': wes_04_collected,
        'wes_03_active': wes_03_active,
        'wes_03_wdevices': wes_03_wdevices,
        'wes_03_collected': wes_03_collected,
        'wes_02_active': wes_02_active,
        'wes_02_wdevices': wes_02_wdevices,
        'wes_02_collected': wes_02_collected,
        'wes_01_active': wes_01_active,
        'wes_01_wdevices': wes_01_wdevices,
        'wes_01_collected': wes_01_collected,
        'wes_kg_active': wes_kg_active,
        'wes_kg_wdevices': wes_kg_wdevices,
        'wes_kg_collected': wes_kg_collected,
        # Data: OKES
        'okes_active_students': okes_active_students,
        'okes_active_wdevices': okes_active_wdevice,
        'okes_inactive_students': okes_inactive_wdevice,
        'okes_05_active': okes_05_active,
        'okes_05_wdevices': okes_05_wdevices,
        'okes_05_collected': okes_05_collected,
        'okes_04_active': okes_04_active,
        'okes_04_wdevices': okes_04_wdevices,
        'okes_04_collected': okes_04_collected,
        'okes_03_active': okes_03_active,
        'okes_03_wdevices': okes_03_wdevices,
        'okes_03_collected': okes_03_collected,
        'okes_02_active': okes_02_active,
        'okes_02_wdevices': okes_02_wdevices,
        'okes_02_collected': okes_02_collected,
        'okes_01_active': okes_01_active,
        'okes_01_wdevices': okes_01_wdevices,
        'okes_01_collected': okes_01_collected,
        'okes_kg_active': okes_kg_active,
        'okes_kg_wdevices': okes_kg_wdevices,
        'okes_kg_collected': okes_kg_collected,
        # Data: BTES
        'btes_active_students': btes_active_students,
        'btes_active_wdevices': btes_active_wdevice,
        'btes_inactive_students': btes_inactive_wdevice,
        'btes_05_active': btes_05_active,
        'btes_05_wdevices': btes_05_wdevices,
        'btes_05_collected': btes_05_collected,
        'btes_04_active': btes_04_active,
        'btes_04_wdevices': btes_04_wdevices,
        'btes_04_collected': btes_04_collected,
        'btes_03_active': btes_03_active,
        'btes_03_wdevices': btes_03_wdevices,
        'btes_03_collected': btes_03_collected,
        'btes_02_active': btes_02_active,
        'btes_02_wdevices': btes_02_wdevices,
        'btes_02_collected': btes_02_collected,
        'btes_01_active': btes_01_active,
        'btes_01_wdevices': btes_01_wdevices,
        'btes_01_collected': btes_01_collected,
        'btes_kg_active': btes_kg_active,
        'btes_kg_wdevices': btes_kg_wdevices,
        'btes_kg_collected': btes_kg_collected,
        # Data: IF
        'if_active_students': if_active_students,
        'if_active_wdevices': if_active_wdevice,
        'if_inactive_students': if_inactive_wdevice,
        'if_12_active': if_12_active,
        'if_12_wdevices': if_12_wdevices,
        'if_12_collected': if_12_collected,
        'if_11_active': if_11_active,
        'if_11_wdevices': if_11_wdevices,
        'if_11_collected': if_11_collected,
        'if_10_active': if_10_active,
        'if_10_wdevices': if_10_wdevices,
        'if_10_collected': if_10_collected,
        'if_09_active': if_09_active,
        'if_09_wdevices': if_09_wdevices,
        'if_09_collected': if_09_collected,
        'if_08_active': if_08_active,
        'if_08_wdevices': if_08_wdevices,
        'if_08_collected': if_08_collected,
        'if_07_active': if_07_active,
        'if_07_wdevices': if_07_wdevices,
        'if_07_collected': if_07_collected,
        'if_06_active': if_06_active,
        'if_06_wdevices': if_06_wdevices,
        'if_06_collected': if_06_collected,
        'if_05_active': if_05_active,
        'if_05_wdevices': if_05_wdevices,
        'if_05_collected': if_05_collected,
        'if_04_active': if_04_active,
        'if_04_wdevices': if_04_wdevices,
        'if_04_collected': if_04_collected,
        'if_03_active': if_03_active,
        'if_03_wdevices': if_03_wdevices,
        'if_03_collected': if_03_collected,
        'if_02_active': if_02_active,
        'if_02_wdevices': if_02_wdevices,
        'if_02_collected': if_02_collected,
        'if_01_active': if_01_active,
        'if_01_wdevices': if_01_wdevices,
        'if_01_collected': if_01_collected,
        'if_kg_active': if_kg_active,
        'if_kg_wdevices': if_kg_wdevices,
        'if_kg_collected': if_kg_collected
    }

    if request.method == 'POST':
        if request.POST.get('action') == 'get-report-detail':
            requested_model = context[request.POST.get('model')].prefetch_related('student')

            if request.POST.get('model').split('_')[1] == 'kg':
                student_grade = 'Kindergarten'
            else:
                student_grade = make_ordinal(request.POST.get('model').split('_')[1]) + " Grade"

            response_context = {
                "title": f"{request.POST.get('model').split('_')[0].upper()} · {student_grade} · {request.POST.get('model').split('_')[2].replace('wdevices', 'With Devices')}",
                "title_tag": request.POST.get('model'),
                "students": {}
            }

            if requested_model:
                for record in requested_model:
                    dictionary = {
                        str(record.id): {
                            "device_id": record.device.id,
                            "device_model": record.device.foreign_model.name,
                            "device_serial": record.device.serial,
                            "student_name": record.student.name,
                            "student_id": record.student.id,
                            "student_location": record.student.location.name,
                            "student_grade": make_ordinal(record.student.grade),
                            "student_status": record.student.status.id if record.student.status else 'None',
                            "form_filled": "None",
                            "expiration": "N/A"
                        }
                    }

                    if DataDistribution.objects.filter(student_id = record.student.id).exists():
                        if DataDistribution.objects.filter(student_id = record.student.id).last().created < timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time())):
                            dictionary[str(record.id)]['form_filled'] = f"{dlmr_year_start.year - 1}-{dlmr_year_start.year}"
                        else:
                            dictionary[str(record.id)]['form_filled'] = f"{dlmr_year_start.year}-{dlmr_year_start.year + 1}"

                    if record.student.status_id == 'SP':
                        sp_record = StudentModelPrograms.objects.filter(student_id = record.student.id).last()
                    else:
                        sp_record = None

                    if sp_record == None:
                        if record.student.location.id == '0011':
                            dictionary[str(record.id)]['expiration'] = constance_config.expiration_btms.strftime('%m-%d-%Y')
                        elif record.device.location.id == '0022':
                            dictionary[str(record.id)]['expiration'] = constance_config.expiration_bes.strftime('%m-%d-%Y')
                        elif record.device.location.id == '0051':
                            dictionary[str(record.id)]['expiration'] = constance_config.expiration_res.strftime('%m-%d-%Y')
                        elif record.device.location.id == '0090':
                            if record.student.grade != '12':
                                dictionary[str(record.id)]['expiration'] = constance_config.expiration_fpc_senior.strftime('%m-%d-%Y')
                            else:
                                dictionary[str(record.id)]['expiration'] = constance_config.expiration_fpc_underclass.strftime('%m-%d-%Y')
                        elif record.student.location.id == '0091':
                            if record.student.grade == '12':
                                dictionary[str(record.id)]['expiration'] = constance_config.expiration_mhs_senior.strftime('%m-%d-%Y')
                            else:
                                dictionary[str(record.id)]['expiration'] = constance_config.expiration_mhs_underclass.strftime('%m-%d-%Y')
                        elif record.student.location.id == '0201':
                            dictionary[str(record.id)]['expiration'] = constance_config.expiration_okes.strftime('%m-%d-%Y')
                        elif record.student.location.id == '0301':
                            dictionary[str(record.id)]['expiration'] = constance_config.expiration_btes.strftime('%m-%d-%Y')
                        elif record.student.location.id == '0401':
                            dictionary[str(record.id)]['expiration'] = constance_config.expiration_itms.strftime('%m-%d-%Y')
                        elif record.student.location.id == '7004':
                            dictionary[str(record.id)]['expiration'] = constance_config.expiration_if.strftime('%m-%d-%Y')
                    else:
                        dictionary[str(record.id)]['expiration'] = sp_record.program.expiration.strftime('%m-%d-%Y')

                    response_context['students'].update(dictionary)

                request.session['requested_model'] = response_context['students']
                html = render_to_string('reports/collections_detail_modal.html', response_context, request)

                return HttpResponse(html)
            else:
                return HttpResponse("Requested model does not exist in the context entries.")

        if request.POST.get('action') == 'get-collection-detail':
            requested_model = context[request.POST.get('model')]

            if request.POST.get('model').split('_')[1] == 'kg':
                student_grade = 'Kindergarten'
            else:
                student_grade = make_ordinal(request.POST.get('model').split('_')[1]) + " Grade"

            response_context = {
                "title": f"{request.POST.get('model').split('_')[0].upper()} · {student_grade} · {request.POST.get('model').split('_')[2].title()}",
                "title_tag": request.POST.get('model'),
                "students": {}
            }

            if 'kg Grade' in response_context['title']:
                response_context['title'].replace('kg Grade', 'Kindergarten')

            if 'active Grade' in response_context['title']:
                response_context['title'].replace('active Grade', 'Active')

            if requested_model:
                for entry in requested_model:
                    dictionary = {
                        str(uuid.uuid4()): {
                            "device_id": entry.device.id,
                            "device_model": entry.device.foreign_model.name,
                            "device_bin": entry.device_bin,
                            "student_name": entry.student.name,
                            "student_id": entry.student.id,
                            "student_location": entry.student.location.name,
                            "student_grade": make_ordinal(entry.student.grade),
                            "student_status": entry.student.status.id if entry.student.status else 'None',
                            "date_collected": entry.created.strftime("%m/%d/%Y"),
                            "author": entry.author.get_full_name()
                        }
                    }

                    response_context['students'].update(dictionary)

                request.session['requested_model'] = response_context['students']
                html = render_to_string('reports/collections_collected_modal.html', response_context, request)

                return HttpResponse(html)
            else:
                return HttpResponse("Requested model does not exist in the context entries.")

    return render(request, 'reports/collections_overview.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrator', 'Staff'])
def export_collections_detail(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_request.csv"'

    data_headers = ['device_id', 'device_model', 'expiration', 'student_name', 'student_id', 'student_location', 'form_filled', 'student_grade']
    data_dictionary = request.session.pop('requested_model')

    if request.POST.get('title_tag') == 'mhs_collected':
        data_headers.append('date_collected')
        data_headers.append('device_bin')

    writer = csv.DictWriter(response, data_headers)
    writer.writeheader()

    for key in data_dictionary:
        writer.writerow({field: data_dictionary[key].get(field) or key for field in data_headers})

    return response

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def device_assignments(request):
    url = request.get_full_path()

    if 'date' in request.GET:
        datetime_string = f'{request.GET.get("date")} 00:00:00'
        datetime_object = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
        current_date = datetime_object
    else:
        current_date = timezone.make_aware(datetime.combine(date.today(), datetime.min.time()))

    start_date = timezone.make_aware(datetime(2020, 7, 13, 0, 0, 0))
    current_date_end = current_date + timedelta(hours = 23, minutes = 59)
    current_datetime = timezone.now()

    device_history = list(Device.history.filter(Q(model__icontains = 'macbook') | Q(model__icontains = 'ipad'), history_date__range = [current_date, current_date_end], owner_id__isnull = False).values_list('owner_id', flat = True))

    students = Student.objects.filter(id__in = device_history)
    students_count = students.count()

    data_dictionary = {}
    data_fields = [
        'student_id', 'student_name', 'student_username', 'student_location_id', 'student_location_alias', 'student_ec',
        'device_id', 'device_model', 'device_location_id', 'device_location_alias', 'device_assigned_by', 'device_assigned_time',
        'l5_issue'
    ]

    for student in students:
        try:
            historical_student = Student.history.filter(id = student.id, history_date__range = [current_date, current_date_end]).latest()
        except:
            try:
                historical_student = Student.history.filter(id = student.id, history_date__range = [timezone.make_aware(start_date), current_date_end]).latest()
            except:
                try:
                    historical_student = Student.history.filter(id = student.id).latest()
                except:
                    student.save()
                    historical_student = Student.history.filter(id = student.id).latest()

        historical_device = Device.history.filter(Q(model__icontains = 'macbook') | Q(model__icontains = 'ipad'), history_date__range = [current_date, current_date_end], owner_id = student.id).latest()

        data_dictionary.update({
            student.id: {
                'student_name': historical_student.name,
                'student_username': historical_student.username,
                'student_grade': historical_student.grade,
                'student_location_id': historical_student.location.id if historical_student.location else 'None',
                'student_location_alias': historical_student.location.alias if historical_student.location else 'None',
                'student_ec': historical_student.role.name if historical_student.role else 'None',
                'device_id': historical_device.id,
                'device_model': historical_device.model,
                'device_location_id': historical_device.location.id if historical_device.location else 'None',
                'device_location_alias': historical_device.location.alias if historical_device.location else 'None',
                'device_assigned_by': historical_device.history_user.get_full_name(),
                'device_assigned_time': historical_device.history_date.strftime('%m/%d/%Y %I:%M %p')
            }
        })

        if L5QDistribution.objects.filter(student_id = historical_student.id).exists():
            data_dictionary[student.id]['l5_issue'] = 'Yes'
        else:
            data_dictionary[student.id]['l5_issue'] = 'No'

    data_json = json.dumps(data_dictionary)

    context = {
        'students_count': students_count,
        # Lists
        'data_fields': data_fields,
        'data_dictionary': data_dictionary,
        'data_json': data_json
    }

    return render(request, 'reports/device_assignments.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def lauper_data(request):
    def get_distribution_data(student_id = None):
        if student_id != None:
            distribution_data = DataDistribution.objects.filter(student_id = student_id)

            if distribution_data.count() > 0:
                if distribution_data.last().updated.date() >= constance_config.dlmr_year_start:
                    return '23-24'
                elif date(2022, 5, 8) < distribution_data.last().updated.date() < constance_config.dlmr_year_start:
                    return '22-23'
                else:
                    return False
            else:
                return False
        else:
            return False

    page = request.GET.get('page', 1)
    url = request.get_full_path()

    locations = Location.objects.exclude(id__in = ['7005', '8000', '8001', '9999']).order_by('name')
    grades = config.GRADE_LEVELS
    yes_no = ['Yes', 'No']

    student_device_ownership = list(StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad')).values_list('student_id', flat = True))

    if 'has_device' in request.GET and request.GET['has_device'] == 'Yes':
        students = StudentModel.objects.filter(id__in = student_device_ownership)
    elif 'has_device' in request.GET and request.GET['has_device'] == 'No':
        students = StudentModel.objects.exclude(id__in = student_device_ownership)
    else:
        students = StudentModel.objects.all()

    allowed_filters = {
        'grade': 'grade',
        'location': 'location_id'
    }

    filters = get_filters(url, allowed_filters)
    filtered_query = students.filter(**filters)
    entries = filtered_query.order_by('-updated')

    paginator = Paginator(entries, 200)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    data_dictionary = {}
    data_fields = [
        'student_id', 'student_name', 'student_username', 'student_grade', 'student_location_id', 'student_status', 'student_location_alias', 'student_ec',
        'devices_owned', 'form_completed', 'payment_completed'
    ]

    for student in entries:
        devices_owned = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), student_id = student.id)

        data_dictionary.update({
            student.id: {
                'student_name': student.name,
                'student_username': student.username,
                'student_grade': student.grade,
                'student_location_id': student.location.id if student.location else None,
                'student_location_alias': student.location.alias if student.location else None,
                'student_status': student.status.id ,
                'student_ec': student.role.name if student.role else None,
                'devices_owned': ', '.join(device.device.id for device in devices_owned) or None,
                'form_completed': get_distribution_data(student.id),
                'payment_completed': True if get_distribution_data(student.id) == '23-24' else False
            }
        })

    data_json = json.dumps(data_dictionary)

    context = {
        # QuerySets
        'locations': locations,
        # Data
        'data_dictionary': data_dictionary,
        'data_json': data_json,
        'data_fields': data_fields,
        # Variables
        'grades': grades,
        'yes_no': yes_no,
        # Search
        'entries': entries
    }

    return render(request, 'reports/lauper_data.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def summer_enrolled(request):
    page = request.GET.get('page', 1)
    url = request.get_full_path()
    current_datetime = timezone.now()

    students = StudentModelPrograms.objects.all().select_related('student', 'student__location', 'student__status', 'program')
    locations = Location.objects.exclude(id__in = ['0000', '0061', '0070', '7005', '7006', '8000', '8001', '9999', 'N998']).order_by('name')
    programs = PersonPrograms.objects.all()
    grades = config.SIDELOAD_GRADE_LEVELS

    allowed_filters = {
        'grade': 'student__grade',
        'location': 'student__location_id',
        'program': 'program'
    }

    filters = get_filters(url, allowed_filters)
    filtered_query = students.filter(**filters)
    entries = filtered_query

    paginator = Paginator(entries, 200)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    data_dictionary = {}
    data_fields = [
        'fleid', 'other_id', 'grade', 'first_name', 'last_name', 'full_name', 'school', 'status', 'program', 'program_start', 'program_end', 'submitted_by', 'form_completed', 'devices_owned'
    ]

    for record in entries:
        if record.student.status.id == 'SP':
            data_dictionary.update({
                record.student.id: {
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

                }
            })

    data_json = json.dumps(data_dictionary)

    context = {
        # Data
        'data_dictionary': data_dictionary,
        'data_json': data_json,
        'data_fields': data_fields,
        'grades': grades,
        # Queries
        'locations': locations,
        'programs': programs,
        # Search
        'entries': entries
    }

    return render(request, 'reports/summer_enrolled.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def device_inactive(request):
    current_datetime = timezone.now()
    dlmr_year_start = constance_config.dlmr_year_start

    def get_distribution_data(student_id = None):
        if student_id != None:
            distribution_data = DataDistribution.objects.filter(student_id = student_id)

            if distribution_data.count() > 0:
                if distribution_data.last().updated >= timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time())):
                    return '21-22'
                elif distribution_data.last().updated < timezone.make_aware(datetime.combine(dlmr_year_start, datetime.min.time())):
                    return '20-21'
                else:
                    return False
            else:
                return False
        else:
            return False

    url = request.get_full_path()
    page = request.GET.get('page', 1)

    locations = Location.objects.exclude(id__in = ['0061', '0070', '7005', '7006', '8000', '8001', '9999', 'N998']).order_by('name')
    entries = StudentDeviceOwnership.objects.select_related('device', 'student').filter(Q(device__foreign_model__name__icontains = 'ipad') | Q(device__foreign_model__name__icontains = 'macbook'), student__isnull = False, student__status_id__in = ['G', 'IA', 'W']).exclude(student__role_id = 'DEL').order_by('-student__withdraw_date', 'student__name')

    if 'location' in request.GET:
        entries = entries.filter(student__location_id = request.GET['location'])

    entries_count = entries.count()
    paginator = Paginator(entries, 45)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    context = {
        # Queryset
        'entries': entries,
        'locations': locations,
        # Variables
        'entries_count': entries_count
    }

    return render(request, 'reports/device_inactive.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def device_delinquent(request):
    dlmr_year_start = constance_config.dlmr_year_start

    def get_delinquent_data(student_id = None):
        historical_data = StudentModel.history.filter(id = student_id, role_id = 'DEL')
        delinquent_date = None

        if historical_data.count() > 0:
            if historical_data.count() == 1:
                delinquent_date = historical_data.latest('history_date').history_date
            elif historical_data.count() > 1:
                delinquent_record = historical_data.latest('history_date')
                is_true = True

                while is_true:
                    if delinquent_record.prev_record != None and delinquent_record.prev_record.role_id == 'DEL':
                        delinquent_date = delinquent_record.prev_record.history_date
                        delinquent_record = delinquent_record.prev_record
                    else:
                        is_true = False
                        break
        else:
            historical_data = Student.history.filter(id = student_id, role_id = 'DEL')

            if historical_data.count() == 1:
                delinquent_date = historical_data.latest('history_date').history_date
            elif historical_data.count() > 1:
                delinquent_record = historical_data.latest('history_date')
                is_true = True

                while is_true:
                    if delinquent_record.prev_record != None and delinquent_record.prev_record.role_id == 'DEL':
                        delinquent_date = delinquent_record.prev_record.history_date
                        delinquent_record = delinquent_record.prev_record
                    else:
                        is_true = False
                        break

        return delinquent_date

    current_datetime = timezone.now()
    url = request.get_full_path()
    page = request.GET.get('page', 1)

    locations = Location.objects.exclude(id__in = ['0061', '0070', '7005', '7006', '8000', '8001', '9999', 'N998']).order_by('name')
    entries = StudentDeviceOwnership.objects.select_related('device', 'student').filter(Q(device__foreign_model__name__icontains = 'ipad') | Q(device__foreign_model__name__icontains = 'macbook'), student__isnull = False, student__role_id = 'DEL').order_by('-student__withdraw_date', 'student__name')

    if 'location' in request.GET:
        entries = entries.filter(student__location_id = request.GET['location'])

    entries_count = entries.count()
    paginator = Paginator(entries, 45)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    delinquent_dates = {}
    for entry in entries:
        delinquent_date = get_delinquent_data(entry.student.id)
        delinquent_dates.update({entry.student.id: delinquent_date.strftime('%m-%d-%Y') if delinquent_date is not None else 'Unknown'})

    context = {
        # Querysets
        'entries': entries,
        'locations': locations,
        # Dictionaries
        'delinquent_dates': delinquent_dates,
        # Variables
        'entries_count': entries_count
    }

    return render(request, 'reports/device_delinquent.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def devito_data(request):
    page = request.GET.get('page', 1)
    url = request.get_full_path()
    current_datetime = timezone.now()

    if 'model' in request.GET:
        students = Student.objects.filter(type = 'F', id__in = Device.objects.filter(foreign_model__id = request.GET.get('model')).values_list('owner_id', flat = True))
    else:
        students = Student.objects.filter(type = 'F', id__in = Device.objects.values_list('owner_id', flat = True))

    locations = Location.objects.exclude(id__in = ['7005', '8000', '8001', '9999']).order_by('name')

    laptop_models = DeviceModel.objects.filter(Q(name__icontains = 'macbook') | Q(name__icontains = '14-fq0013dx'))
    tablet_models = DeviceModel.objects.filter(name__icontains = 'ipad')
    hotspot_models = DeviceModel.objects.filter(Q(name__icontains = 'coolpad') | Q(name__icontains = 'duraforce') | Q(name__icontains = 'e6') | Q(name__icontains = 'jetpack') | Q(name__icontains = 'zone') | Q(name__icontains = 'r850'))

    allowed_filters = {
        'location': 'location_id'
    }

    filters = get_filters(url, allowed_filters)
    entries = students.filter(**filters).order_by('name')

    paginator = Paginator(entries, 200)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    data_dictionary = {}
    data_fields = [
        'student_id', 'student_name', 'student_username', 'student_grade', 'student_location_id', 'student_location_alias',
        'devices_owned',
        'form_completed', 'payment_completed'
    ]

    for student in entries:
        devices_owned = Device.objects.filter(Q(model__icontains = 'macbook') | Q(model__icontains = 'ipad'), owner_id = student.id)

        data_dictionary.update({
            student.id: {
                'student_name': student.name,
                'student_username': student.username,
                'student_location_id': student.location.id if student.location else None,
                'student_location_alias': student.location.alias if student.location else None,
                'devices_owned': ', '.join(device.id for device in devices_owned) or None
            }
        })

    data_json = json.dumps(data_dictionary)

    context = {
        # QuerySets
        'locations': locations,
        'laptop_models': laptop_models,
        'tablet_models': tablet_models,
        'hotspot_models': hotspot_models,
        # Data
        'data_dictionary': data_dictionary,
        'data_json': data_json,
        'data_fields': data_fields,
        # Search
        'entries': entries
    }

    return render(request, 'reports/devito_data.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def device_history(request):
    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        historical_search_query = get_query(query_string, ['device__id', 'device__serial'])
        collections_search_query = get_query(query_string, ['device__id', 'device__serial'])

        last_historical_entry = StudentDeviceOwnership.history.filter(historical_search_query).select_related('student', 'device').last()
        collections_entry = NewDataCollection.objects.filter(collections_search_query).last()
    else:
        last_historical_entry = False
        collections_entry = False

    context = {
        # Search
        'last_historical_entry': last_historical_entry,
        'collections_entry': collections_entry
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

    return render(request, 'reports/device_history.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator'])
def device_bins(request):
    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['id', 'serial', 'bin'])
        entries = Device.objects.filter(search_query).order_by('id')
    else:
        entries = None

    page = request.GET.get('page', 1)

    def get_collections_data(device_id):
        collections_record = NewDataCollection.objects.filter(device__id = device_id).last()

        if collections_record != None:
            return {
                'collect_date': collections_record.updated.strftime('%m-%d-%Y'),
                'collect_bin': collections_record.device_bin,
                'collect_author': collections_record.author.get_full_name()
            }
        else:
            return None

    def get_staged_data(device_id):
        staged_record = DataStaging.objects.filter(device_bpi = device_id).last()

        if staged_record != None:
            return {
                'staged_date': staged_record.updated.strftime('%m-%d-%Y'),
                'staged_bin': staged_record.device_bin
            }
        else:
            return None

    if entries != None:
        paginator = Paginator(entries, 50)

        try:
            entries = paginator.page(page)
        except PageNotAnInteger:
            entries = paginator.page(1)
        except EmptyPage:
            entries = paginator.page(paginator.num_pages)

        device_data = {}

        for device in entries:
            device_data.update({
                device.id: {
                    'device_id': device.id,
                    'device_serial': device.serial,
                    'device_model': device.foreign_model.name,
                    'device_location': device.location.name,
                    'device_bin': device.bin,
                    'collections': get_collections_data(device.id),
                    'staging': get_staged_data(device.id)
                }
            })
    else:
        device_data = None

    context = {
        'entries': device_data
    }

    return render(request, 'reports/device_bins.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff', 'IDOnly'])
def temporary_ids(request):
    if 'IDOnly' in list(request.user.groups.values_list('name', flat = True)):
        id_only = True
    else:
        id_only = False

    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['student__id', 'student__name', 'student__username'])
        entries = StudentModelIDLog.objects.filter(search_query).order_by('-date').select_related('student', 'student__location', 'author')
    else:
        entries = StudentModelIDLog.objects.all().order_by('-date').select_related('student', 'student__location', 'author')

    url = request.get_full_path()
    allowed_filters = {
        'location': 'student__location__id'
    }

    filters = get_filters(url, allowed_filters)
    entries = entries.filter(**filters).order_by('-date')

    page = request.GET.get('page', 1)
    paginator = Paginator(entries, 200)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    context = {
        # Queries
        'entries': entries,
        'locations': Location.objects.exclude(id__in = ['0000', '0061', '0070', '7005', '7006', '8000', '8001', '9999']),
        # Variables
        'id_only': id_only
    }

    if request.method == 'POST':
        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

    return render(request, 'reports/temporary_ids.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def case_inventory(request):
    entries = StudentModel.objects.all().select_related('location')

    page = request.GET.get('page', 1)
    paginator = Paginator(entries, 50)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    has_case = []

    for entry in entries:
        if StudentChargerOwnership.objects.filter(student = entry, charger__type_id = '.5m1case').exists():
            has_case.append(entry.id)

    print(has_case)

    context = {
        # Data
        'has_case': has_case,
        # Queries
        'entries': entries
    }

    return render(request, 'reports/case_inventory.html', context)
