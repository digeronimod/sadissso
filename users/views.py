# Python
import datetime, json
from datetime import date, timedelta
from distutils.util import strtobool
from urllib.parse import urlsplit, urlunsplit
# Django
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import View
from json import loads
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
# Plugins
from constance import config as constance_config
# SADIS
from common import dates as school_dates
from .decorators import allowed_users
from .models import MediaParentChoice, MedicalNeeds, NewDataCollection, DataDistribution, DataSchoolPay, DataStaging, StaffModel, L5QDistribution, Student, StudentModel, StudentChargerOwnership, StudentDeviceOwnership, StudentAppointments, StudentFines, StudentModelPrograms, StudentRole, StudentStatuses, StudentTransfers, ContactValidation, EmergencyContactInfo, SchoolClinicServices
from common.device import set_owner_by_force
from inventory.models import Device, Charger, ChargerCondition, ChargerType, FineTypes, FineSubtypes, Location, Note
from inventory.utilities import get_filters, get_query, is_blank, is_not_blank, queue_html_email, Qurl
from sadis import config
from sadis.api import api_iiq as iiq
from sadis.api import api_msb as msb

def userPage(request):
   context = {}
   return render(request, 'users/detail_students2.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def home(request):
    if 'IDOnly' in list(request.user.groups.values_list('name',flat = True)):
        id_only = True
    else:
        id_only = False

    students = Student.objects.all()
    page = request.GET.get('page', 1)
    url = request.get_full_path()

    current_datetime = timezone.now()

    locations = Location.objects.filter(id__in = config.LOCATIONS).order_by('name')
    locations_sideload = Location.objects.filter(id__in = config.SIDELOAD_LOCATIONS).order_by('name')

    grades = config.GRADE_LEVELS
    grades_sideload = config.SIDELOAD_GRADE_LEVELS

    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['id', 'name', 'username'])
        entries = students.filter(search_query).order_by('name')
    else:
        entries = students.order_by('name')

    paginator = Paginator(entries, 50)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    dlm_registration = {}

    for user in entries:
        if DataDistribution.objects.filter(student_id = user.id).exists():
            data = DataDistribution.objects.get(student_id = user.id)

            if datetime.datetime.date(data.created) >= constance_config.dlmr_year_start:
                form_completed = True
            else:
                form_completed = False

            if bool(data.payment_complete):
                payment_completed = True
            else:
                payment_completed = False
        else:
            form_completed = False
            payment_completed = False

        if form_completed and payment_completed:
            dlm_registration[user.id] = True
        else:
            dlm_registration[user.id] = False

    context = {
        # Querys
        'locations': locations,
        'locations_sideload': locations_sideload,
        # Dictionaries
        'current_datetime': current_datetime,
        'dlm_registration': dlm_registration,
        'grades': grades,
        'grades_sideload': grades_sideload,
        # Variables
        'iiq_sync_datetime': constance_config.sync_iiq,
        # Search
        'entries': entries,
        'id_only': id_only
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

        if request.POST.get('action') == 'sideload-student-submit':
            student_name = f'{request.POST.get("student_first_name")} {request.POST.get("student_last_name")}'

            Student.objects.create(
                id = request.POST.get('student_other_id'),
                name = student_name,
                username = request.POST.get('student_username'),
                location_id = request.POST.get('student_location_id'),
                type = 'S',
                status = '1',
                foreign_status_id = 'N',
                grade = request.POST.get('student_grade'),
                role_id = 'OTO',
                remote = 0,
                birthdate = datetime.datetime.strptime(f"{request.POST.get('student_birthdate')}", '%m/%d/%Y').date()
            )

            response_data['student_name'] = student_name

            email_context = {
                'student_name': student_name,
                'student_id': request.POST.get('student_other_id'),
                'student_username': request.POST.get('student_username'),
                'student_location': Location.objects.get(id = request.POST.get('student_location_id')).name,
                'student_grade': request.POST.get('student_grade')
            }

            if bool(request.POST.get("parent_present")):
                email_context.update({
                    'parent_email': request.POST.get('parent_email'),
                    'parent_phone': request.POST.get('parent_phone')
                })

                if is_not_blank(email_context['parent_email']):
                    queue_html_email(recipient = email_context['parent_email'], subject = 'Welcome', template = 'users/sideload_parent_email.html', context = email_context)

            device_ticket = iiq.create_new_student_device_ticket(request.POST.get('student_location_id'))

            if device_ticket != None:
                ticket_description = f"Student Information\n\nStudent ID: {email_context['student_id']}\nStudent Name: {email_context['student_name']}\nStudent Username: {email_context['student_username']}\nStudent School: {email_context['student_location']}\nStudent Grade: {email_context['student_grade']}"

                if 'parent_email' in email_context.keys():
                    ticket_description = ticket_description + f"\n\nParent Email: {email_context['parent_email']}\nParent Phone: {email_context['parent_phone']}"

                iiq.assign_ticket_agent_and_team(device_ticket['ticket_id'], device_ticket['agent_uuid'], device_ticket['team_uuid'])
                iiq.change_ticket_description_and_location(device_ticket['ticket_id'], device_ticket['location_uuid'], ticket_description)

                queue_html_email(recipient = request.POST.get('student_counselor'), subject = 'Student DLMR Enrollment', template = 'users/sideload_counselor_email.html', context = email_context)
            else:
                queue_html_email(recipient = 'new-student-needs-device@flaglerschools.incidentiq.com', subject = 'FS | Sideloaded Student Needs Device', template = 'users/sideload_iiq_email.html', context = email_context)

            response_data['response'] = True
            return JsonResponse(response_data)

        if request.POST.get('action') == 'student-transfer-search':
            student_query = request.POST.get('transfer_search')
            student_search = get_query(student_query, ['id', 'name'])
            student_entries = Student.objects.filter(student_search)

            results = {}
            for student in student_entries:
                results.update({
                    student.id: {
                        'id': student.id,
                        'text': f'{student.id}: {student.name}'
                    }
                })

            return JsonResponse(results)

        if request.POST.get('action') == 'transfer-student-submit':
            transfer_student = Student.objects.get(id = request.POST.get('student_id'))
            transfer_record = None
            transfer_ticket = None

            if transfer_student:
                transfer_record = StudentTransfers.objects.create(
                    student = transfer_student,
                    author = request.user,
                    transfer_from = Location.objects.get(id = request.POST.get('transfer_from_id')),
                    transfer_to = Location.objects.get(id = request.POST.get('transfer_to_id'))
                )

                response_data['result'] = 1
                response_data['student_name'] = transfer_student.name

                transfer_student.foreign_status_id = 'IT'
                transfer_student.save()
            else:
                response_data['result'] = 0

            if response_data['result'] == 1:
                transfer_ticket = iiq.create_new_student_transfer_ticket(request.POST.get('transfer_to_id'))

            if transfer_ticket != None:
                transfer_record.iiq_id = transfer_ticket['ticket_id']
                transfer_record.save()

                email_context = {
                    'student_name': transfer_student.name,
                    'student_id': transfer_student.id,
                    'student_username': transfer_student.username,
                    'student_from_location': transfer_student.location.name,
                    'student_to_location': transfer_record.transfer_to.name,
                    'student_grade': transfer_student.grade
                }

                ticket_description = f"Student Information\n\nStudent ID: {email_context['student_id']}\nStudent Name: {email_context['student_name']}\nStudent Username: {email_context['student_username']}\nStudent Grade: {email_context['student_grade']}\n\nTransferring From: {email_context['student_from_location']}\nTransferring To: {email_context['student_to_location']}"

                iiq.assign_ticket_agent_and_team(transfer_ticket['ticket_id'], transfer_ticket['agent_uuid'], transfer_ticket['team_uuid'])
                iiq.change_ticket_description_and_location(transfer_ticket['ticket_id'], transfer_ticket['location_uuid'], ticket_description)

                try:
                    iiq.change_ticket_owner_and_user(transfer_ticket['ticket_id'], 'ba4403b5-38af-ea11-9b05-0003ffe429a2', transfer_student.iiq_id)
                except:
                    pass

                if bool(request.POST.get('notify_admin')):
                    for email in transfer_ticket['notify_recipient']:
                        queue_html_email(recipient = email, subject = 'Student DLM Transfer', template = 'users/transfer_student_email.html', context = email_context)

            return JsonResponse(response_data)

    return render(request, 'users/index.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def home_students(request):
    if 'IDOnly' in list(request.user.groups.values_list('name',flat = True)):
        id_only = True
    else:
        id_only = False

    students = StudentModel.objects.all()
    page = request.GET.get('page', 1)

    current_datetime = timezone.now()

    locations = Location.objects.filter(id__in = config.LOCATIONS).order_by('name')
    locations_sideload = Location.objects.filter(id__in = config.SIDELOAD_LOCATIONS).order_by('name')

    grades = config.GRADE_LEVELS
    grades_sideload = config.SIDELOAD_GRADE_LEVELS

    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['id', 'unique_id', 'name', 'username'])
        entries = students.filter(search_query).order_by('name')
    else:
        entries = []

    paginator = Paginator(entries, 45)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    dlm_registration = {}

    for user in entries:
        if DataDistribution.objects.filter(student_id = user.id).exists():
            data = DataDistribution.objects.get(student_id = user.id)

            if datetime.datetime.date(data.created) >= constance_config.dlmr_year_start:
                form_completed = True
            else:
                form_completed = False

            if bool(data.payment_complete):
                payment_completed = True
            else:
                payment_completed = False
        else:
            form_completed = False
            payment_completed = False

        if form_completed and payment_completed:
            dlm_registration[user.id] = True
        else:
            dlm_registration[user.id] = False

    context = {
        # Querys
        'locations': locations,
        'locations_sideload': locations_sideload,
        # Dictionaries
        'current_datetime': current_datetime,
        'dlm_registration': dlm_registration,
        'grades': grades,
        'grades_sideload': grades_sideload,
        # Variables
        'edfi_sync_datetime': constance_config.sync_edfi,
        # Search
        'entries': entries,
        'id_only': id_only
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

        if request.POST.get('action') == 'sideload-student-submit':
            student_name = f'{request.POST.get("student_first_name")} {request.POST.get("student_last_name")}'

            StudentModel.objects.create(
                id = request.POST.get('student_other_id'),
                name = student_name,
                username = request.POST.get('student_username'),
                location_id = request.POST.get('student_location_id'),
                status_id = 'N',
                grade = request.POST.get('student_grade'),
                role_id = 'OTO',
                remote = 0,
                birthdate = datetime.datetime.strptime(f"{request.POST.get('student_birthdate')}", '%m/%d/%Y').date()
            )

            response_data['student_name'] = student_name

            email_context = {
                'student_name': student_name,
                'student_id': request.POST.get('student_other_id'),
                'student_username': request.POST.get('student_username'),
                'student_location': Location.objects.get(id = request.POST.get('student_location_id')).name,
                'student_grade': request.POST.get('student_grade')
            }

            if bool(request.POST.get("parent_present")):
                email_context.update({
                    'parent_email': request.POST.get('parent_email'),
                    'parent_phone': request.POST.get('parent_phone')
                })

                if is_not_blank(email_context['parent_email']):
                    queue_html_email(recipient = email_context['parent_email'], subject = 'Welcome', template = 'users/sideload_parent_email.html', context = email_context)

            device_ticket = iiq.create_new_student_device_ticket(request.POST.get('student_location_id'))

            if device_ticket != None:
                ticket_description = f"Student Information\n\nStudent ID: {email_context['student_id']}\nStudent Name: {email_context['student_name']}\nStudent Username: {email_context['student_username']}\nStudent School: {email_context['student_location']}\nStudent Grade: {email_context['student_grade']}"

                if ('parent_email' in email_context.keys()) and is_not_blank(email_context['parent_email']):
                    ticket_description = ticket_description + f"\n\nParent Email: {email_context['parent_email']}\nParent Phone: {email_context['parent_phone']}"

                iiq.assign_ticket_agent_and_team(device_ticket['ticket_id'], device_ticket['agent_uuid'], device_ticket['team_uuid'])
                iiq.change_ticket_description_and_location(device_ticket['ticket_id'], device_ticket['location_uuid'], ticket_description)

                if is_not_blank(request.POST.get('student_counselor')):
                    queue_html_email(recipient = request.POST.get('student_counselor'), subject = 'Student DLMR Enrollment', template = 'users/sideload_counselor_email.html', context = email_context)
            else:
                queue_html_email(recipient = 'new-student-needs-device@flaglerschools.incidentiq.com', subject = 'FS | Sideloaded Student Needs Device', template = 'users/sideload_iiq_email.html', context = email_context)

            response_data['response'] = True
            return JsonResponse(response_data)

        if request.POST.get('action') == 'student-transfer-search':
            student_query = request.POST.get('transfer_search')
            student_search = get_query(student_query, ['id', 'unique_id', 'name'])
            student_entries = StudentModel.objects.filter(student_search)

            results = {}
            for student in student_entries:
                results.update({
                    student.id: {
                        'id': student.id,
                        'text': f'{student.id}: {student.name}'
                    }
                })

            return JsonResponse(results)

        if request.POST.get('action') == 'transfer-student-submit':
            transfer_student = StudentModel.objects.get(id = request.POST.get('student_id'))
            transfer_record = None
            transfer_ticket = None

            if transfer_student:
                transfer_record = StudentTransfers.objects.create(
                    student = transfer_student,
                    author = request.user,
                    transfer_from = Location.objects.get(id = request.POST.get('transfer_from_id')),
                    transfer_to = Location.objects.get(id = request.POST.get('transfer_to_id'))
                )

                response_data['result'] = 1
                response_data['student_name'] = transfer_student.name

                transfer_student.status_id = 'IT'
                transfer_student.save()
            else:
                response_data['result'] = 0

            if response_data['result'] == 1:
                transfer_ticket = iiq.create_new_student_transfer_ticket(request.POST.get('transfer_to_id'))

            if transfer_ticket != None:
                transfer_record.iiq_id = transfer_ticket['ticket_id']
                transfer_record.save()

                email_context = {
                    'student_name': transfer_student.name,
                    'student_id': transfer_student.id,
                    'student_username': transfer_student.username,
                    'student_from_location': transfer_student.location.name,
                    'student_to_location': transfer_record.transfer_to.name,
                    'student_grade': transfer_student.grade
                }

                ticket_description = f"Student Information\n\nStudent ID: {email_context['student_id']}\nStudent Name: {email_context['student_name']}\nStudent Username: {email_context['student_username']}\nStudent Grade: {email_context['student_grade']}\n\nTransferring From: {email_context['student_from_location']}\nTransferring To: {email_context['student_to_location']}"

                iiq.assign_ticket_agent_and_team(transfer_ticket['ticket_id'], transfer_ticket['agent_uuid'], transfer_ticket['team_uuid'])
                iiq.change_ticket_description_and_location(transfer_ticket['ticket_id'], transfer_ticket['location_uuid'], ticket_description)

                try:
                    iiq.change_ticket_owner_and_user(transfer_ticket['ticket_id'], 'ba4403b5-38af-ea11-9b05-0003ffe429a2', transfer_student.iiq_id)
                except:
                    pass

                if bool(request.POST.get('notify_admin')):
                    for email in transfer_ticket['notify_recipient']:
                        queue_html_email(recipient = email, subject = 'Student DLM Transfer', template = 'users/transfer_student_email.html', context = email_context)

            return JsonResponse(response_data)

    return render(request, 'users/index_students.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def home_employees(request):
    page = request.GET.get('page', 1)
    current_datetime = timezone.now()

    employees = StaffModel.objects.all()
    locations = Location.objects.filter(id__in = config.LOCATIONS).order_by('name')

    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['id', 'unique_id', 'name', 'username'])
        entries = employees.filter(search_query).order_by('name')
    else:
        entries = []

    paginator = Paginator(entries, 45)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    context = {
        # Querys
        'locations': locations,
        # Dictionaries
        'current_datetime': current_datetime,
        # Variables
        'edfi_sync_datetime': constance_config.sync_edfi,
        # Search
        'entries': entries
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

    return render(request, 'users/index_employees.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def detail_students(request, id):
    if 'IDOnly' in list(request.user.groups.values_list('name',flat = True)):
        id_only = True
    else:
        id_only = False

    student_query = StudentModel.objects.filter(pk = id).select_related('location', 'location_code', 'role', 'status', 'studentmodelprograms', 'student_transfer')
    student = student_query.first()

    if request.user.groups.filter(name__in = ['Administrator']).exists():
        is_admin = True
    else:
        is_admin = False

    if request.user.groups.filter(name__in = ['Super Administrator']).exists():
        is_superuser = True
    else:
        is_superuser = False

    super_admin_list = ['digeronimod', 'leed', 'thibodeaut', 'kopacha', 'phillipst']

    if request.user.username in super_admin_list:
        is_super_admin = True
    else:
        is_super_admin = False

    if constance_config.msb_enabled:
        student_invoices = msb.get_invoices_by_student_id(student.id)
    else:
        student_invoices = []

    student_unpaid_fee_list = {}
    student_paid_fee_list = {}

    if bool(student_invoices):
        count = 1

        for invoice in student_invoices:
            for key, value in invoice.items():
                if key == 'invoiceItems':
                    for item in value:
                        dictionary = {
                            count: {
                                'id': invoice['invoiceID'],
                                'status': item['status'],
                                'name': item['feeName'],
                                'amount': item['invoiceItemPrice'],
                                'amount_paid': int(item['invoiceItemPrice']) - int(item['invoiceItemRemainingAmount']),
                                'created': datetime.datetime.fromisoformat(item['createdDate'].replace('Z', '')).strftime('%m-%d-%Y')
                            }
                        }

                        if dictionary[count]['status'] == 'PENDING':
                            student_unpaid_fee_list.update(dictionary)
                        elif dictionary[count]['status'] == 'CLOSED':
                            student_paid_fee_list.update(dictionary)

                        count += 1

    current_datetime = timezone.now()
    fine_subtypes = FineSubtypes.objects.all()
    fine_types = FineTypes.objects.all()
    roles = StudentRole.objects.all()
    statuses = StudentStatuses.objects.all()

    devices = StudentDeviceOwnership.objects.filter(student_id = student.id)
    chargers = StudentChargerOwnership.objects.filter(student_id = student.id)
    notes = Note.objects.filter(item_id = student.id).order_by('-created')
    student_fines = StudentFines.objects.filter(student_id = student.id)
    student_fines_unpaid = student_fines.filter(status = 'UP')
    student_fines_unpaid_total = 0

    for fine in student_fines_unpaid:
        student_fines_unpaid_total += fine.get_value()

    historical_fines = StudentFines.history.filter(student_id = student.id)
    historical_notes = Note.history.filter(item_id = student.id)

    try:
        summer_program_record = StudentModelPrograms.objects.get(student = student)
    except:
        summer_program_record = None

    assigned_devices = {}
    for device in devices:
        assigned_devices.update({
            device.device.id: {
                'manufacturer': device.device.manufacturer,
                'model': device.device.foreign_model.name,
                'serial': device.device.serial,
                'date_assigned': (device.date if device.date else 'Unknown'),
                'assigner': (device.author.username if device.author else 'Unknown')
            }
        })

        if summer_program_record == None:
            if student.location.id == '0011':
                assigned_devices[device.device.id]['expiration'] = constance_config.expiration_btms
            elif student.location.id == '0022':
                assigned_devices[device.device.id]['expiration'] = constance_config.expiration_bes
            elif student.location.id == '0051':
                assigned_devices[device.device.id]['expiration'] = constance_config.expiration_res
            elif student.location.id == '0090':
                if student.grade != '12':
                    assigned_devices[device.device.id]['expiration'] = constance_config.expiration_fpc_senior
                else:
                    assigned_devices[device.device.id]['expiration'] = constance_config.expiration_fpc_underclass
            elif student.location.id == '0091':
                if student.grade == '12':
                    assigned_devices[device.device.id]['expiration'] = constance_config.expiration_mhs_senior
                else:
                    assigned_devices[device.device.id]['expiration'] = constance_config.expiration_mhs_underclass
            elif student.location.id == '0201':
                assigned_devices[device.device.id]['expiration'] = constance_config.expiration_okes
            elif student.location.id == '0301':
                assigned_devices[device.device.id]['expiration'] = constance_config.expiration_btes
            elif student.location.id == '0401':
                assigned_devices[device.device.id]['expiration'] = constance_config.expiration_itms
            elif student.location.id == '7004':
                assigned_devices[device.device.id]['expiration'] = constance_config.expiration_if
        else:
            assigned_devices[device.device.id]['expiration'] = summer_program_record.program.expiration

    if len(assigned_devices) > 0:
        assignment_warning = True
    else:
        assignment_warning = False

    assigned_chargers = {}
    for charger in chargers:
        assigned_chargers.update({
            charger.charger.id: {
                'name': charger.charger.type.name,
                'adapter': bool(charger.charger.adapter),
                'cord': bool(charger.charger.cord),
                'assigned_date': 'Unknown',
                'assigned_author': (charger.author.username if charger.author else 'Unknown')
            }
        })

        if charger.date and is_not_blank(str(charger.date)):
            assigned_chargers[charger.charger.id]['assigned_date'] = charger.date.strftime("%m-%d-%Y")

    if DataStaging.objects.filter(student_id = student.id).exists():
        sdata_object = DataStaging.objects.get(student_id = student.id)

        if sdata_object.device_bin != None:
            staging_data = {
                'bin': sdata_object.device_bin,
                'bpi': sdata_object.device_bpi
            }

            try:
                sdata_history = DataStaging.history.filter(student_id = student.id).latest()

                staging_data.update({
                    'author': sdata_history.history_user.get_full_name(),
                    'created': sdata_history.history_date
                })
            except:
                staging_data.update({
                    'author': None,
                    'created': None
                })
        else:
            staging_data = False
    else:
        staging_data = False

    if L5QDistribution.objects.filter(student_id = student.id, created__isnull = False, completed = 0, tech_required = 1, tech_completed = 0).exists():
        l5qdata = L5QDistribution.objects.filter(student_id = student.id, created__isnull = False, completed = 0, tech_required = 1, tech_completed = 0).latest('created')
    else:
        l5qdata = None

    if DataDistribution.objects.filter(student_id = student.id).exists():
        ddata = DataDistribution.objects.get(student_id = student.id)
    else:
        ddata = None

    if ddata:
        dlmr_year_start = constance_config.dlmr_year_start

        if DataDistribution.objects.filter(student_id = student.id).last().created > school_dates.START_2023:
            ddata_date = '23-24'
        elif school_dates.START_2022 < DataDistribution.objects.filter(student_id = student.id).last().created < school_dates.END_2023:
            ddata_date = '22-23'
        else:
            ddata_date = False
    else:
        ddata_date = False

    # if ddata_date in ['21-22', '22-23']: <!-- disabled 5-5-2023 -->
    if ddata_date in ['22-23', '23-24']:
        ddata_date_valid = True
    else:
        ddata_date_valid = False

    if NewDataCollection.objects.filter(student_id = student.id).exists():
        cdata = NewDataCollection.objects.filter(student_id = student.id).latest('updated')
    else:
        cdata = None

    schoolpay_data = DataSchoolPay.objects.filter(student_id = student.id)

    if MediaParentChoice.objects.filter(student_id = student.id).exists():
        mpcdata = MediaParentChoice.objects.filter(student_id = student.id).last()

    if student.status_id == 'IT':
        try:
            transfer_record = StudentTransfers.objects.get(student = student)
        except:
            transfer_record = None
    else:
        transfer_record = None

    context = {
        # QuerySets
        'assignment_warning': assignment_warning,
        'assigned_devices': assigned_devices,
        'ddata': ddata,
        'ddata_date': ddata_date,
        'ddata_date_valid': ddata_date_valid,
        'cdata': cdata,
        'staging_data': staging_data,
        'student_unpaid_fee_list': student_unpaid_fee_list,
        'student_paid_fee_list': student_paid_fee_list,
        'schoolpay_data': schoolpay_data,
        'fine_types': fine_types,
        'fine_subtypes': fine_subtypes,
        'statuses': statuses,
        'l5qdata': l5qdata,
        'notes': notes,
        'roles': roles,
        'student': student,
        'student_email': f'{student.username}@flaglercps.org',
        'student_fines': student_fines,
        'student_fines_unpaid': student_fines_unpaid,
        'student_fines_unpaid_total': student_fines_unpaid_total,
        'transfer_record': transfer_record,
        'summer_program_record': summer_program_record,
        'charger_types': ChargerType.objects.all(),
        'charger_conditions': ChargerCondition.objects.all(),
        # Variables
        'current_school_year_abbrev': constance_config.current_school_year_abbrev,
        'assigned_devices': assigned_devices,
        'assigned_chargers': assigned_chargers,
        'current_datetime': current_datetime,
        'is_admin': is_admin,
        'is_superuser': is_superuser,
        'is_super_admin': is_super_admin,
        # History
        'historical_fines': historical_fines,
        'historical_notes': historical_notes,
        'id_only': id_only
    }

    data = False

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('action') == 'resend-registration-email':
            current_datetime = timezone.now()
            distribution_data = DataDistribution.objects.get(student_id = student.id)

            student_first_name = student.name.split(" ", 1)[0]
            student_last_name = student.name.split(" ", 1)[1]

            resend_address = request.POST.get('resend_address')

            email_context = {
                'student': student,
                'current_datetime': current_datetime.strftime('%Y-%m-%d'),
                'student_first_name': distribution_data.student_first_name,
                'student_grade': distribution_data.student_grade,
                'student_id': distribution_data.student_id,
                'student_last_name': distribution_data.student_last_name,
                'student_location': Location.objects.get(id = distribution_data.student_location_id),
                'parent_address': distribution_data.parent_address,
                'parent_email': distribution_data.parent_email,
                'parent_name': distribution_data.parent_name,
                'parent_phone': distribution_data.parent_phone,
                'parent_signature': distribution_data.parent_signature
            }

            if resend_address != distribution_data.parent_email:
                distribution_data.parent_email = resend_address
                distribution_data.save()

                email_context['parent_email'] = resend_address

                queue_html_email(recipient = resend_address, subject = 'DLM Registration Confirmation', template = 'dlmr/email.html', context = email_context)
            else:
                queue_html_email(recipient = email_context['parent_email'], subject = 'DLM Registration Confirmation', template = 'dlmr/email.html', context = email_context)

            response_data['response'] = True
            return JsonResponse(response_data)
        elif request.POST.get('action') == 'update-staging-data':
            staging_data_exists = DataStaging.objects.filter(student_id = student.id).exists()

            if staging_data_exists:
                staging_data = DataStaging.objects.get(student_id = student.id)
                staging_data.device_bpi = request.POST.get('device_bpi')
                staging_data.device_bin = request.POST.get('device_bin')

                staging_data.save()
            else:
                staging_data = DataStaging.objects.create(student_id = student.id, device_bpi = request.POST.get('device_bpi'), device_bin = request.POST.get('device_bin'))

            try:
                device = Device.objects.get(id = staging_data.device_bpi)
                device.bin = staging_data.device_bin

                device.save()
            except:
                pass

            if 'iiq_ticket_number' in request.POST.keys():
                submitted_ticket_number = request.POST.get('iiq_ticket_number')
                l5q_entry = L5QDistribution.objects.filter(student_id = student.id, created__isnull = False, completed = 0, tech_required = 1, tech_completed = 0).latest('created')
                iiq_ticket_id = l5q_entry.iiq_ticket
                iiq_ticket_number = iiq.get_ticket_number(iiq_ticket_id)

                if submitted_ticket_number == iiq_ticket_number:
                    l5q_entry.tech_completed = 1
                    l5q_entry.iiq_ticket_number = iiq_ticket_number
                    l5q_entry.save()

                    response_data['ticket_matched'] = 'Y'
                else:
                    response_data['ticket_matched'] = 'N'
            else:
                response_data['ticket_matched'] = 'NA'

            response_data['response'] = True
            return JsonResponse(response_data)
        elif request.POST.get('action') == 'sync-assets-submit':
            if student.status_id == 'N':
                owned_devices = StudentDeviceOwnership.objects.filter(student_id = student.id)

                for device in owned_devices:
                    iiq.set_owner_by_force(student, request.user)

                student.status_id = 'A'
                student.save()

            asset_list = iiq.get_user_assets(student.iiq_id)

            if len(asset_list) > 0:
                for asset_id in asset_list:
                    response_data[asset_id] = student.id

                    set_owner_by_force(Device.objects.get(id = asset_id), student, request.user)

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'get-iiq-id-submit':
            iiq_data = iiq.get_user_uuid(student.id)
            response_data.update(iiq_data)

            student.iiq_id = iiq_data['iiq_id']
            student.save()

            if student.iiq_id != None:
                if student.status_id == 'N':
                    owned_devices = StudentDeviceOwnership.objects.filter(student_id = student.id)

                    for device in owned_devices:
                        iiq.set_owner_by_force(student, request.user)

                    student.status_id = 'A'
                    student.save()

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'modify-assets-search':
            device_query = request.POST.get('search')
            device_search = get_query(device_query, ['id'])
            device_entries = Device.objects.filter(device_search)

            results = {}
            for device in device_entries:
                results.update({
                    device.id: {
                        'id': device.id,
                        'text': f'{device.id}: {device.model}'
                    }
                })

            return JsonResponse(results)
        elif request.POST.get('action') == 'get-internal-asset':
            asset_id = request.POST.get('asset_id')
            asset_object = Device.objects.get(id = asset_id)

            asset_data = {
                'id': asset_object.id,
                'manufacturer': asset_object.manufacturer,
                'model': asset_object.model,
                'serial': asset_object.serial,
                'roles': [role.id for role in asset_object.role.all()]
            }

            return JsonResponse(asset_data)
        elif request.POST.get('action') == 'modify-assets-submit':
            add_assets_list = json.loads(request.POST.get('assign_assets_list'))
            remove_assets_list = json.loads(request.POST.get('unassign_assets_list'))

            if student.status_id == 'N':
                for asset_id in remove_assets_list:
                    unassign_device = Device.objects.get(id = asset_id)
                    unassign_device.owner_id = None
                    unassign_device.owner_assign_date = None
                    unassign_device.owner_assign_author = request.user
                    unassign_device.save()

                    response_data['unassign_response'] = True

                for asset_id in add_assets_list:
                    modify_owner = Device.objects.get(id = asset_id)

                    if modify_owner.owner_id == student.id:
                        pass
                    else:
                        modify_owner.owner_id = student.id
                        modify_owner.owner_assign_date = timezone.now()
                        modify_owner.owner_assign_author = request.user
                        modify_owner.save()

                    response_data['assign_response'] = True
            else:
                for asset_id in remove_assets_list:
                    unassign_device = Device.objects.get(id = asset_id)

                    if is_blank(unassign_device.iiq_id):
                        asset_uuid = iiq.get_asset_uuid(asset_id)

                        unassign_device.iiq_id = asset_uuid
                        unassign_device.save()
                    else:
                        asset_uuid = unassign_device.iiq_id

                    iiq.unassign_asset_from_user(asset_uuid, student.iiq_id)
                    unassign_device.owner_id = None
                    unassign_device.owner_assign_date = None
                    unassign_device.owner_assign_author = request.user
                    unassign_device.save()

                    response_data['unassign_response'] = True

                for asset_id in add_assets_list:
                    iiq_response = iiq.get_asset_status(asset_id)

                    if iiq_response['status'] == 200:
                        post_data = iiq.assign_asset_to_user(iiq_response['asset_uuid'], student.iiq_id)

                        if post_data.status_code == 200:
                            modify_owner = Device.objects.get(id = asset_id)

                            if modify_owner.owner_id == student.id:
                                pass
                            else:
                                modify_owner.owner_id = student.id
                                modify_owner.owner_assign_date = timezone.now()
                                modify_owner.owner_assign_author = request.user
                                modify_owner.save()

                            response_data['assign_response'] = True
                        else:
                            response_data['assign_response'] = True
                    elif iiq_response['status'] == 409:
                        response_data['assign_response'] = False

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'change-student-ec':
            role_id = request.POST.get('role_id')

            if is_not_blank(role_id):
                student.role_id = role_id
                student.save()

                response_data['response'] = True
            else:
                response_data['response'] = False

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'change-student-status':
            status_id = request.POST.get('status_id')

            if is_not_blank(status_id):
                student.status_id = status_id

                student.save()

                response_data['response'] = True
            else:
                response_data['response'] = False

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'complete-student-transfer':
            if transfer_record == None:
                transfer_record = StudentTransfers.objects.get(student = student)

            student.location_id = transfer_record.transfer_to.id
            student.status_id = 'A'

            student.save()

            for device in devices:
                device.location_id = student.location_id
                device.save()

                asset_uuid = iiq.get_asset_uuid(device.id)
                iiq.assign_asset_to_user_by_force(asset_uuid, student.iiq_id)

            iiq.change_user_location(student.iiq_id, student.location.iiq_id)
            transfer_record.delete()

            response_data['response'] = True

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'delete-note-submit':
            note_id = request.POST.get('to_delete')

            note_object = Note.objects.get(pk = note_id)
            note_object.delete()

            response_data['response'] = True
            return JsonResponse(response_data)

    return render(request, 'users/detail_students.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def collections(request):
    from users.models import StudentDeviceOwnership

    def remove_url_parameters(url):
        return urlunsplit(urlsplit(url)._replace(query = '', fragment = ''))

    current_datetime = datetime.datetime.now()
    locations = Location.objects.filter(id__in = config.SIDELOAD_LOCATIONS).order_by('name')
    ownerships = StudentDeviceOwnership.objects.select_related('student', 'device')

    page = request.GET.get('page', 1)
    grades = config.GRADE_LEVELS

    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['student__id', 'student__name', 'student__username'])
        entries = ownerships.filter(search_query)
    else:
        entries = None

    if entries != None:
        paginator = Paginator(entries, 50)

        try:
            entries = paginator.page(page)
        except PageNotAnInteger:
            entries = paginator.page(1)
        except EmptyPage:
            entries = paginator.page(paginator.num_pages)

    # Get charger information
    chargers = {}
    if entries != None:
        for record in entries:
            chargers.update({
                record.student.id: []
            })

            chargers_assigned = StudentChargerOwnership.objects.filter(student_id = record.student.id)

            for charger in chargers_assigned:
                chargers[record.student.id].append(charger.charger.type.id)

    current_datetime = timezone.now()

    if current_datetime > constance_config.expiration_collections:
        collections_expired = True
    else:
        collections_expired = False

    context = {
        # QuerySets
        'locations': locations,
        # Variables
        'current_datetime': current_datetime,
        'collections_expired': collections_expired,
        'grades': grades,
        # Lists/Dictionaries
        'chargers': chargers,
        # Search
        'entries': entries
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('action') == 'get-device-owner':
            query_string = request.POST.get('device_identifier')
            search_query = get_query(query_string, ['device__id', 'device__serial'])
            ownership_records = StudentDeviceOwnership.objects.filter(search_query).select_related('student', 'device')

            if ownership_records.count() > 0:
                ownership_record = ownership_records.first()
                cleaned_url = remove_url_parameters(request.get_full_path())
                redirect_url = Qurl(cleaned_url).add('search', value = ownership_record.student.name).get()

                response_data.update({
                    'success': True,
                    'redirect_url': redirect_url
                })

                return JsonResponse(response_data)
            else:
                response_data.update({
                    'success': False
                })

                return JsonResponse(response_data)

    return render(request, 'users/collections.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def distributions(request):
    from common.charger import set_owner as set_charger_owner
    from common.device import set_owner as set_device_owner

    students = StudentModel.objects.all()
    page = request.GET.get('page', 1)
    url = request.get_full_path()

    location_exclude = ['7005', '8000', '8001', '9999', 'N998']
    locations = Location.objects.exclude(id__in = location_exclude).order_by('name')
    grades = config.GRADE_LEVELS

    allowed_filters = {
        'grade': 'grade',
        'location': 'location_id'
    }

    filters = get_filters(url, allowed_filters)
    filtered_query = students.filter(**filters)

    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['id', 'name', 'username'])
        entries = filtered_query.filter(search_query).order_by('-updated')
    else:
        entries = filtered_query.order_by('-updated')

    paginator = Paginator(entries, 50)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    chargers = {}
    form_payment = {}
    bpi_bin = {}
    appointments = {}

    for user in entries:
        form_payment.update({
            user.id: {}
        })

        chargers.update({
            user.id: []
        })

        appointments.update({
            user.id: None
        })

        chargers_assigned = StudentChargerOwnership.objects.filter(student_id = user.id)

        for charger in chargers_assigned:
            chargers[user.id].append(charger.charger.type.id)

        if StudentAppointments.objects.filter(student_id = user.id).exists():
            appointments[user.id] = StudentAppointments.objects.filter(student_id = user.id).latest('created').event.event_start

        ddata_exists = DataDistribution.objects.filter(student_id = user.id).exists()

        if ddata_exists:
            ddata = DataDistribution.objects.get(student_id = user.id)

            if datetime.datetime.date(ddata.updated) > constance_config.dlmr_year_start:
                form_payment[user.id]['form'] = True
                form_payment[user.id]['form_date'] = '23-24'
            else:
                form_payment[user.id]['form'] = False
                form_payment[user.id]['form_date'] = '22-23'

            if bool(ddata.payment_complete) and (datetime.datetime.date(ddata.updated) > constance_config.dlmr_year_start):
                form_payment[user.id]['paid'] = True
            else:
                form_payment[user.id]['paid'] = False
        else:
            form_payment[user.id]['form'] = False
            form_payment[user.id]['form_date'] = False
            form_payment[user.id]['paid'] = False

        staging_data_exists = DataStaging.objects.filter(student_id = user.id, updated__gte = date(2021, 5, 18)).exists()

        if staging_data_exists:
            staging_data = DataStaging.objects.get(student_id = user.id)

            if staging_data.updated != None:
                if datetime.datetime.date(staging_data.updated) >= datetime.date(2021, 5, 18):
                    device_tag = staging_data.device_bpi
                    device_bin = staging_data.device_bin
                else:
                    device_tag = None
                    device_bin = None
            else:
                device_tag = None
                device_bin = None
        else:
            device_tag = None
            device_bin = None

        bpi_bin[user.id] = {
            'bpi': device_tag,
            'bin': device_bin,
            'owned': False
        }

        try:
            device_record = StudentDeviceOwnership.objects.filter(device_id = bpi_bin[user.id]['bpi']).first()

            if device_record.student_id == user.id:
                bpi_bin[user.id]['owned'] = True
        except:
            pass

    last_updated = students.latest('updated').updated
    current_datetime = timezone.now()

    if current_datetime > constance_config.expiration_distribution:
        distributions_expired = True
    else:
        distributions_expired = False

    start_datetime = datetime.datetime(2021, 7, 13, 0, 0, 0)
    today_datetime_start = datetime.datetime.combine(date.today(), datetime.datetime.min.time())
    today_datetime_end = today_datetime_start + timedelta(hours = 23, minutes = 59)

    devices_assigned_today = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'macbook') | Q(device__foreign_model__name__icontains = 'ipad'), date__range = [timezone.make_aware(today_datetime_start), timezone.make_aware(today_datetime_end)]).count()
    macbook_assigned_total = StudentDeviceOwnership.objects.filter(device__foreign_model__name__icontains = 'macbook', date__gte = constance_config.dlmr_year_start).count()
    ipad_assigned_total = StudentDeviceOwnership.objects.filter(device__foreign_model__name__icontains = 'ipad', date__gte = constance_config.dlmr_year_start).count()

    context = {
        # QuerySets
        'locations': locations,
        # Variables
        'bpi_bin': bpi_bin,
        'chargers': chargers,
        'appointments': appointments,
        'charger_types': ChargerType.objects.all(),
        'charger_conditions': ChargerCondition.objects.exclude(id__in = ['D', 'UW']),
        'current_datetime': current_datetime,
        'devices_assigned_today': devices_assigned_today,
        'distributions_expired': distributions_expired,
        'ipad_assigned_total': ipad_assigned_total,
        'macbook_assigned_total': macbook_assigned_total,
        'form_payment': form_payment,
        'grades': grades,
        'last_updated': last_updated,
        # Search
        'entries': entries
    }

    if request.method == 'POST':
        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

        response_data = {}

        if request.POST.get('action') == 'assign-bpi-to-student':
            the_student = StudentModel.objects.get(id = request.POST.get('student_to_assign'))
            the_student_uuid = the_student.iiq_id

            asset_uuid = iiq.get_asset_uuid(request.POST.get('bpi_to_assign'))
            the_device = Device.objects.get(id = request.POST.get('bpi_to_assign'))
            device_has_case = bool(strtobool(request.POST.get('assign_case')))

            the_device.location_id = the_student.location_id
            the_device.owner_assign_date = timezone.now()
            the_device.owner_assign_author = request.user
            the_device.has_case = device_has_case
            the_device.save()

            assign_device = set_device_owner(the_device, the_student, request.user)
            assign_response = json.loads(assign_device.content)

            if assign_response['code'] == 200:
                assign_note = f"Device BPI {the_device.id} assigned to student during Distributions."

                if device_has_case:
                    assign_note += " Device was issued without a case."
                else:
                    assign_note += " Device was issued with a case."

                Note.objects.create(item_id = the_student.id, body = assign_note, author = request.user)

            if bool(strtobool(request.POST.get('assign_charger'))):
                assign_charger_type = request.POST.get('assign_charger_type')
                assign_charger_condition = request.POST.get('assign_charger_condition')

                if assign_charger_condition == None or assign_charger_condition == '':
                    assign_charger_condition = 'N'

                charger_type = ChargerType.objects.get(id = assign_charger_type)
                author = request.user

                try:
                    charger_exists = Charger.objects.filter(id = StudentChargerOwnership.objects.filter(charger__type = charger_type, charger__location = Location.objects.get(id = the_student.location.id), student_id__isnull = True).first().charger_id).exists()
                except:
                    charger_exists = False

                if charger_exists:
                    existing_charger = Charger.objects.get(id = StudentChargerOwnership.objects.filter(charger__type = charger_type, charger__location = Location.objects.get(id = the_student.location.id), student_id__isnull = True).first().charger_id)
                else:
                    existing_charger = None

                if existing_charger != None:
                    set_charger_owner(existing_charger, the_student, request.user)
                else:
                    created_charger = Charger.objects.create(
                        type = charger_type,
                        status = ChargerCondition.objects.get(id = assign_charger_condition),
                        location = Location.objects.get(id = the_student.location.id)
                    )

                    created_charger.save()

                    set_charger_owner(created_charger, the_student, request.user)

                note_concatenation = f'Charger {charger_type.name} added during Distributions.'

                Note.objects.create(item_id = the_student.id, body = note_concatenation, author = request.user, attached_id = None)

            response_data['assign_response'] = True

            return JsonResponse(response_data)

    return render(request, 'users/distributions.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def distributions_l5q(request):
    from common.charger import set_owner as set_charger_owner
    from common.device import set_owner as set_device_owner

    students = L5QDistribution.objects.filter(completed = 0)
    page = request.GET.get('page', 1)
    url = request.get_full_path()

    location_excludes = ['7005', '8000', '8001', '9999', 'N998']
    location_excludes_sideload = ['0000', '0061', '7005', '7006', '8000', '8001', '9999', 'N998']

    locations = Location.objects.exclude(id__in = location_excludes).order_by('name')
    locations_sideload = Location.objects.exclude(id__in = location_excludes_sideload).order_by('name')

    grades = config.GRADE_LEVELS
    grades_sideload = ['KG', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    allowed_filters = {
        'grade': 'grade',
        'location': 'location_id'
    }

    filters = get_filters(url, allowed_filters)
    filtered_query = students.filter(**filters)
    entries = filtered_query.order_by('created')
    entries_count = entries.count()

    form_payment = {}
    bpi_bin = {}
    for user in entries:
        ddata_exists = DataDistribution.objects.filter(student_id = user.student.id).exists()

        if ddata_exists:
            ddata = DataDistribution.objects.get(student_id = user.student.id)

            if datetime.datetime.date(ddata.updated) > datetime.date(2022, 5, 1):
                form_filled = True
            else:
                form_filled = False

            if bool(ddata.payment_complete):
                payment_made = True
            else:
                payment_made = False
        else:
            form_filled = False
            payment_made = False

        form_payment[user.student.id] = {
            'form': form_filled,
            'paid': payment_made
        }

        staging_data_exists = DataStaging.objects.filter(student_id = user.student.id).exists()

        if staging_data_exists:
            staging_data = DataStaging.objects.get(student_id = user.student.id)

            if datetime.datetime.date(staging_data.updated) > datetime.date(2022, 5, 1):
                device_tag = staging_data.device_bpi
                device_bin = staging_data.device_bin
            else:
                device_tag = None
                device_bin = None
        else:
            device_tag = None
            device_bin = None

        bpi_bin[user.student.id] = {
            'bpi': device_tag,
            'bin': device_bin,
            'owned': False
        }

        try:
            sdata_history = DataStaging.history.filter(student_id = user.student.id).latest()

            bpi_bin[user.student.id].update({
                'stager': sdata_history.history_user.username
            })
        except:
            bpi_bin[user.student.id].update({
                'stager': 'None'
            })

        try:
            get_device_owner = StudentDeviceOwnership.objects.get(device_id = bpi_bin[user.student.id]['bpi']).student_id

            if get_device_owner == user.student.id:
                bpi_bin[user.student.id]['owned'] = True
        except:
            pass

    current_datetime = timezone.now()

    start_datetime = datetime.datetime(2020, 7, 13, 0, 0, 0)
    today_datetime_start = datetime.datetime.combine(date.today(), datetime.datetime.min.time())
    today_datetime_end = today_datetime_start + timedelta(hours = 23, minutes = 59)

    devices_assigned_today = Device.history.filter(Q(model__icontains = 'macbook') | Q(model__icontains = 'ipad'), owner_id__isnull = False, history_date__range = [timezone.make_aware(today_datetime_start), timezone.make_aware(today_datetime_end)]).count()
    macbook_assigned_total = Device.history.filter(model__icontains = 'macbook', owner_id__isnull = False, history_date__range = [timezone.make_aware(start_datetime), timezone.make_aware(today_datetime_end)]).count()
    ipad_assigned_total = Device.history.filter(model__icontains = 'ipad', owner_id__isnull = False, history_date__range = [timezone.make_aware(start_datetime), timezone.make_aware(today_datetime_end)]).count()

    context = {
        # QuerySets
        'locations': locations,
        'locations_sideload': locations_sideload,
        'charger_types': ChargerType.objects.all(),
        'charger_conditions': ChargerCondition.objects.exclude(id__in = ['D', 'UW']),
        # Variables
        'bpi_bin': bpi_bin,
        'current_datetime': current_datetime,
        'devices_assigned_today': devices_assigned_today,
        'ipad_assigned_total': ipad_assigned_total,
        'macbook_assigned_total': macbook_assigned_total,
        'form_payment': form_payment,
        'grades': grades,
        'grades_sideload': grades_sideload,
        # Search
        'entries': entries,
        'entries_count': entries_count
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('action') == 'assign-bpi-to-student':
            asset_uuid = iiq.get_asset_uuid(request.POST.get('bpi_to_assign'))

            the_student = StudentModel.objects.get(id = request.POST.get('student_to_assign'))
            the_student_uuid = the_student.iiq_id

            queue_id = request.POST.get('queue_id')

            asset_uuid = iiq.get_asset_uuid(request.POST.get('bpi_to_assign'))
            the_device = Device.objects.get(id = request.POST.get('bpi_to_assign'))
            device_has_case = bool(strtobool(request.POST.get('assign_case')))

            the_device.location_id = the_student.location_id
            the_device.owner_assign_date = timezone.now()
            the_device.owner_assign_author = request.user
            the_device.has_case = device_has_case
            the_device.save()

            assign_device = set_device_owner(the_device, the_student, request.user)
            assign_response = json.loads(assign_device.content)

            if assign_response['code'] == 200:
                assign_note = f"Device BPI {the_device.id} assigned to student during Distributions."

                if device_has_case:
                    assign_note += " Device was issued with a case."
                else:
                    assign_note += " Device was issued without a case."

                Note.objects.create(item_id = the_student.id, body = assign_note, author = request.user)

            queue_object = L5QDistribution.objects.get(id = queue_id)
            queue_object.completed = 1
            queue_object.tech_completed = 1
            queue_object.save()

            if bool(strtobool(request.POST.get('assign_charger'))):
                assign_charger_type = request.POST.get('assign_charger_type')
                assign_charger_condition = request.POST.get('assign_charger_condition')

                if assign_charger_condition == None or assign_charger_condition == '':
                    assign_charger_condition = 'N'

                charger_type = ChargerType.objects.get(id = assign_charger_type)
                author = request.user

                try:
                    charger_exists = Charger.objects.filter(id = StudentChargerOwnership.objects.filter(charger__type = charger_type, charger__location = Location.objects.get(id = the_student.location.id), student_id__isnull = True).first().charger_id).exists()
                except:
                    charger_exists = False

                if charger_exists:
                    existing_charger = Charger.objects.get(id = StudentChargerOwnership.objects.filter(charger__type = charger_type, charger__location = Location.objects.get(id = the_student.location.id), student_id__isnull = True).first().charger_id)
                else:
                    existing_charger = None

                if existing_charger != None:
                    set_charger_owner(existing_charger, the_student, request.user)
                else:
                    created_charger = Charger.objects.create(
                        type = charger_type,
                        status = ChargerCondition.objects.get(id = assign_charger_condition),
                        location = Location.objects.get(id = the_student.location.id)
                    )

                    set_charger_owner(created_charger, the_student, request.user)

                note_concatenation = f'Charger {charger_type.name} added during Distributions.'

                Note.objects.create(item_id = the_student.id, body = note_concatenation, author = request.user, attached_id = None)

            response_data['assign_response'] = True

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'existing-student-search':
            student_query = request.POST.get('search')
            student_search = get_query(student_query, ['id', 'name'])
            student_entries = StudentModel.objects.filter(student_search)

            results = {}
            for student in student_entries:
                results.update({
                    student.id: {
                        'id': student.id,
                        'text': f'{student.id}: {student.name}'
                    }
                })

            return JsonResponse(results)
        elif request.POST.get('action') == 'l5q-existing-submit':
            try:
                student = StudentModel.objects.get(id = request.POST.get('student_id'))
            except:
                student = None

            issue_type = request.POST.get('student_issue')

            if student != None:
                if issue_type == 'R' or issue_type == 'NI':
                    L5QDistribution.objects.create(student_id = request.POST.get('student_id'), issue_type = issue_type, vehicle_description = request.POST.get('student_vehicle'), author = request.user)

                    response_data['student_name'] = student.name
                    response_data['response'] = True
                elif issue_type == 'ND':
                    L5QDistribution.objects.create(student_id = request.POST.get('student_id'), issue_type = issue_type, tech_required = 1, vehicle_description = request.POST.get('student_vehicle'), author = request.user)

                    response_data['student_name'] = student.name
                    response_data['response'] = True
                else:
                    response_data['response'] = False
            else:
                response_data['response'] = False

            return JsonResponse(response_data)

    return render(request, 'users/distributions_l5q.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def distributions_tq(request):
    students = L5QDistribution.objects.filter(tech_required = 1, tech_completed = 0)
    page = request.GET.get('page', 1)
    url = request.get_full_path()
    current_datetime = timezone.now()
    entries = students.order_by('created')

    context = {
        # Variables
        'current_datetime': current_datetime,
        # Search
        'entries': entries
    }

    return render(request, 'users/distributions_tq.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def distributions_sq(request):
    current_date = datetime.datetime.combine(date.today(), datetime.datetime.min.time())
    current_date_end = current_date + timedelta(hours = 23, minutes = 59)

    students = L5QDistribution.objects.filter(created__range = [current_date, current_date_end], completed = 0)
    students_completed = L5QDistribution.objects.filter(created__range = [current_date, current_date_end], completed = 1).order_by('-updated')[:30]
    url = request.get_full_path()

    entries = students.order_by('created')
    entries_count = entries.filter(completed = 0).count()

    form_payment = {}
    bpi_bin = {}
    for user in entries:
        ddata_exists = DataDistribution.objects.filter(student_id = user.student.id).exists()

        if ddata_exists:
            ddata = DataDistribution.objects.get(student_id = user.student.id)

            if datetime.datetime.date(ddata.updated) > datetime.date(2020, 3, 15):
                form_filled = True
            else:
                form_filled = False

            if bool(ddata.payment_complete):
                payment_made = True
            else:
                payment_made = False
        else:
            form_filled = False
            payment_made = False

        form_payment[user.student.id] = {
            'form': form_filled,
            'paid': payment_made
        }

        staging_data_exists = DataStaging.objects.filter(student_id = user.student.id).exists()

        if staging_data_exists:
            staging_data = DataStaging.objects.get(student_id = user.student.id)

            if datetime.datetime.date(staging_data.updated) > datetime.date(2020, 3, 15):
                device_tag = staging_data.device_bpi
                device_bin = staging_data.device_bin
            else:
                device_tag = None
                device_bin = None
        else:
            device_tag = None
            device_bin = None

        bpi_bin[user.student.id] = {
            'bpi': device_tag,
            'bin': device_bin,
            'owned': False
        }

        try:
            sdata_history = DataStaging.history.filter(student_id = user.student.id).latest()

            bpi_bin[user.student.id].update({
                'stager': sdata_history.history_user.username
            })
        except:
            bpi_bin[user.student.id].update({
                'stager': 'None'
            })

        try:
            get_device_owner = Device.objects.get(id = bpi_bin[user.student.id]['bpi']).owner_id

            if get_device_owner == user.student.id:
                bpi_bin[user.student.id]['owned'] = True
        except:
            pass

    for user in students_completed:
        ddata_exists = DataDistribution.objects.filter(student_id = user.student.id).exists()

        if ddata_exists:
            ddata = DataDistribution.objects.get(student_id = user.student.id)

            if datetime.datetime.date(ddata.updated) > datetime.date(2020, 3, 15):
                form_filled = True
            else:
                form_filled = False

            if bool(ddata.payment_complete):
                payment_made = True
            else:
                payment_made = False
        else:
            form_filled = False
            payment_made = False

        form_payment[user.student.id] = {
            'form': form_filled,
            'paid': payment_made
        }

        staging_data_exists = DataStaging.objects.filter(student_id = user.student.id).exists()

        if staging_data_exists:
            staging_data = DataStaging.objects.get(student_id = user.student.id)

            if datetime.datetime.date(staging_data.updated) > datetime.date(2020, 3, 15):
                device_tag = staging_data.device_bpi
                device_bin = staging_data.device_bin
            else:
                device_tag = None
                device_bin = None
        else:
            device_tag = None
            device_bin = None

        bpi_bin[user.student.id] = {
            'bpi': device_tag,
            'bin': device_bin,
            'owned': False
        }

        try:
            sdata_history = DataStaging.history.filter(student_id = user.student.id).latest()

            bpi_bin[user.student.id].update({
                'stager': sdata_history.history_user.username
            })
        except:
            bpi_bin[user.student.id].update({
                'stager': 'None'
            })

        try:
            get_device_owner = Device.objects.get(id = bpi_bin[user.student.id]['bpi']).owner_id

            if get_device_owner == user.student.id:
                bpi_bin[user.student.id]['owned'] = True
        except:
            pass

    current_datetime = timezone.now()

    start_datetime = datetime.datetime(2020, 7, 13, 0, 0, 0)
    today_datetime_start = datetime.datetime.combine(date.today(), datetime.datetime.min.time())
    today_datetime_end = today_datetime_start + timedelta(hours = 23, minutes = 59)

    devices_assigned_today = Device.history.filter(Q(model__icontains = 'macbook') | Q(model__icontains = 'ipad'), owner_id__isnull = False, history_date__range = [timezone.make_aware(today_datetime_start), timezone.make_aware(today_datetime_end)]).count()
    macbook_assigned_total = Device.history.filter(model__icontains = 'macbook', owner_id__isnull = False, history_date__range = [timezone.make_aware(start_datetime), timezone.make_aware(today_datetime_end)]).count()
    ipad_assigned_total = Device.history.filter(model__icontains = 'ipad', owner_id__isnull = False, history_date__range = [timezone.make_aware(start_datetime), timezone.make_aware(today_datetime_end)]).count()

    context = {
        # Variables
        'bpi_bin': bpi_bin,
        'current_datetime': current_datetime,
        'devices_assigned_today': devices_assigned_today,
        'ipad_assigned_total': ipad_assigned_total,
        'macbook_assigned_total': macbook_assigned_total,
        'form_payment': form_payment,
        # Search
        'entries': entries,
        'entries_count': entries_count,
        'students_completed': students_completed
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('action') == 'assign-bpi-to-student':
            pass
        elif request.POST.get('action') == 'existing-student-search':
            student_query = request.POST.get('search')
            student_search = get_query(student_query, ['name'])
            student_entries = StudentModel.objects.filter(student_search)

            results = {}
            for student in student_entries:
                results.update({
                    student.id: {
                        'id': student.id,
                        'text': f'{student.id}: {student.name}'
                    }
                })

            return JsonResponse(results)
        elif request.POST.get('action') == 'l5q-existing-submit':
            issue_type = request.POST.get('student_issue')
            issue_student = StudentModel.objects.get(id = request.POST.get('student_id'))

            if issue_type == 'R' or issue_type == 'NI':
                L5QDistribution.objects.create(student_id = issue_student.id, issue_type = issue_type, vehicle_description = request.POST.get('student_vehicle'), author = request.user)

                response_data['response'] = True
            elif issue_type == 'ND':
                L5QDistribution.objects.create(student_id = issue_student.id, issue_type = issue_type, tech_required = 1, iiq_ticket = new_device_ticket['ticket_id'], vehicle_description = request.POST.get('student_vehicle'), author = request.user)

                response_data['response'] = True
            else:
                response_data['response'] = False

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'l5q-new-submit':
            issue_type = request.POST.get('student_issue')
            student_name = f'{request.POST.get("student_first_name")} {request.POST.get("student_last_name")}'

            new_student = StudentModel.objects.create(
                id = request.POST.get('student_other_id'),
                name = student_name,
                username = request.POST.get('student_username'),
                location_id = request.POST.get('student_location_id'),
                status_id = 'N',
                grade = request.POST.get('student_grade'),
                role_id = 'OTO'
            )

            new_device_ticket = iiq.create_new_student_device_ticket(StudentModel.objects.get(id = request.POST.get('student_id')).location.id)
            create_l5q_record = L5QDistribution.objects.create(student_id = new_student.pk, issue_type = 'NS', tech_required = 1, iiq_ticket = new_device_ticket, vehicle_description = request.POST.get('student_vehicle'), author = request.user)
            response_data['response'] = True

            return JsonResponse(response_data)

    return render(request, 'users/distributions_sq.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrator', 'Staff'])
def device_receipt(request, id):
    student = get_object_or_404(StudentModel, pk = id)
    current_school_year = f"{constance_config.current_school_year_start.year}-{constance_config.current_school_year_end.year}"

    context = {
        'current_datetime': timezone.now(),
        'current_school_year': current_school_year,
        'device_bpi': 'TEST1234',
        'device_model': 'MacBook Pro (2018, 4-Port)',
        'device_assessment_message': 'MacBook handed in for summer refresh, damage present: none. Issued power adapter not returned: student keeping over the summer.',
        'student_address': '19 Blare Castle Dr., Palm Coast, FL 32137',
        'student_name': student.name
    }

    return render(request, 'users/collections_email.html', context)

@csrf_exempt
def contact_validation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        parent_name = data['parent_name']
        parent_email = data['parent_email']
        parent_phone = data['parent_phone']
        parent_id_state = data['parent_id_state']
        parent_id_number = data['parent_id_number']
        student_id = str(data['student_id'])

        contact_validation = ContactValidation(
            parent_name=parent_name,
            parent_email=parent_email,
            parent_phone=parent_phone,
            parent_id_state=parent_id_state,
            parent_id_number=parent_id_number,
            student_id=student_id
        )
        contact_validation.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
    
@csrf_exempt
def emergency_contact_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        emergency_contact_info = EmergencyContactInfo(
            student_id=data['student_id'],
            fam_1_parent_1_name=data['fam_1_parent_1_name'],
            fam_1_parent_1_cell_phone=data['fam_1_parent_1_cell_phone'],
            fam_1_parent_1_daytime_phone=data['fam_1_parent_1_daytime_phone'],
            fam_1_parent_2_name=data['fam_1_parent_2_name'],
            fam_1_parent_2_cell_phone=data['fam_1_parent_2_cell_phone'],
            fam_1_parent_2_daytime_phone=data['fam_1_parent_2_daytime_phone'],
            fam_1_parent_1_email=data['fam_1_parent_1_email'],
            fam_1_parent_2_email=data['fam_1_parent_2_email'],
            fam_1_residence=data['fam_1_residence'],
            fam_1_mailing=data['fam_1_mailing'],
            fam_2_parent_1_name=data['fam_2_parent_1_name'],
            fam_2_parent_1_cell_phone=data['fam_2_parent_1_cell_phone'],
            fam_2_parent_1_daytime_phone=data['fam_2_parent_1_daytime_phone'],
            fam_2_parent_2_name=data['fam_2_parent_2_name'],
            fam_2_parent_2_cell_phone=data['fam_2_parent_2_cell_phone'],
            fam_2_parent_2_daytime_phone=data['fam_2_parent_2_daytime_phone'],
            fam_2_email=data['fam_2_email'],
            fam_2_residence=data['fam_2_residence'],
            fam_2_mailing=data['fam_2_mailing'],
            custody_paperwork=data['custody_paperwork'],
            pickup_5_name=data['pickup_5_name'],
            pickup_5_phone=data['pickup_5_phone'],
            pickup_5_relationship=data['pickup_5_relationship'],
            pickup_6_name=data['pickup_6_name'],
            pickup_6_phone=data['pickup_6_phone'],
            pickup_6_relationship=data['pickup_6_relationship'],
            pickup_7_name=data['pickup_7_name'],
            pickup_7_phone=data['pickup_7_phone'],
            pickup_7_relationship=data['pickup_7_relationship'],
        )
        emergency_contact_info.save()
        return JsonResponse({'success': True})
    else:
        return redirect('home')
    
@csrf_exempt
def medical_needs(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        medical_needs = MedicalNeeds(
            student_id=data['student_id'],
            allergies=data['allergies'],
            allergic_to=data['allergic_to'],
            glasses_or_contacts=data['glasses_or_contacts'],
            hearing_aids=data['hearing_aids'],
            physician_name=data['physician_name'],
            physician_phone=data['physician_phone'],
        )
        medical_needs.save()
        return JsonResponse({'success': True})
    else:
        return redirect('home')
    
@csrf_exempt
def school_clinic_services(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        school_clinic_services = SchoolClinicServices(
            student_id=data['student_id'],
            basic_first_aid=data['basic_first_aid'],
            minor_wound_care=data['minor_wound_care'],
            minor_eye_irritation=data['minor_eye_irritation'],
            minor_bites_and_stings=data['minor_bites_and_stings'],
            minor_upset_stomach=data['minor_upset_stomach'],
            check_for_rashes=data['check_for_rashes'],
            clinic_services_electronic_signature=data['clinic_services_electronic_signature'],
            clinic_services_checkbox=data['clinic_services_checkbox'],
        )
        school_clinic_services.save()
        return JsonResponse({'success': True})
    else:
        return redirect('home')
    
@csrf_exempt
def media_parent_choice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        media_parent_choice = MediaParentChoice(
            student_id=data['student_id'],
            media_choice_level=data['media_choice_level'],
            media_choice_electronic_signature=data['media_choice_electronic_signature'],
            media_choice_checkbox=data['media_choice_checkbox'],
        )
        media_parent_choice.save()
        return JsonResponse({'success': True})
    else:
        return redirect('home')
