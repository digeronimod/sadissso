#! /usr/bin/python3
# Python
import datetime, uuid, json
from distutils.util import strtobool
# Django
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
# SADIS
import common.device as device_utility
import common.charger as charger_utility
from .common import add_note_to_user, archive_dlmr_record
from .decorators import allowed_users
from .models import DataDistribution, DataStaging, StudentModel, StudentModelIDLog, StudentChargerOwnership, StudentDeviceOwnership, StudentModelPrograms
from inventory.models import Charger, ChargerCondition, ChargerType, Device, DeviceAssessment, FineTypes, FineSubtypes, Location, Note, PersonPrograms
from inventory.utilities import is_blank, is_not_blank, make_ordinal, queue_html_email
from sadis import config as sadis_config
from constance import config as constance_config
from sadis.api import api_iiq as iiq
from sadis.api import api_msb as msb

response_data = {
    'response_code': None,
    'response_message': None
}

response_template = {
    'code': 0,
    'status': 'None',
    'data': {
        'message': 'No message.'
    }
}

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def add_alert(request):
    response_data['response_code'] = request.GET.get('alert_code')
    response_data['response_message'] = request.GET.get('alert_body')

    if response_data['response_code'] != 200:
        response_data['response_message'] = f"Error {response_data['response_code']}: An unknown error occurred and your changes may not have been saved."

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def add_note(request):
    student = StudentModel.objects.get(id = request.GET.get('student_id'))
    note_content = request.GET.get('note_body')

    Note.objects.create(item_id = student.id, body = note_content, author = request.user)

    if student.iiq_id != None:
        iiq.prepend_user_notes(student.iiq_id, note_content, request.user.username)

        response_data['response_code'] = 200
    else:
        try:
            iiq_id = iiq.get_user_uuid(student.id)
            iiq.prepend_user_notes(iiq_id, note_content, request.user.username)

            response_data['response_code'] = 200
        except:
            response_data['response_code'] = 404

    if response_data['response_code'] == 404:
        response_data['response_message'] = f"Unable to locate {student.name} in IncidentIQ using the ID number ({student.id})."

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def add_fine(request):
    user = StudentModel.objects.get(id = request.POST.get('student_id'))

    fine_type = FineTypes.objects.get(alias = request.POST.get('fine_type_id'))
    fine_subtype = FineSubtypes.objects.get(alias = request.POST.get('fine_subtype_id'))
    fine_note = request.POST.get('fine_note')

    if request.POST.get('fine_device_id') == 'NA':
        device_id = 'N/A'
    else:
        device_id = request.POST.get('fine_device_id')

    if (fine_type == None or fine_type == 'FINE') or fine_type.value == None:
        fine_amount = fine_subtype.value
    else:
        fine_amount = fine_type.value

    if device_id != 'N/A':
        fine_description = f"{fine_type} for Device {device_id}"
    else:
        fine_description = f"{fine_type}"

    fine_item = {
        'fine_type': fine_type.name,
        'fine_subtype': fine_subtype.name,
        'fine_amount': fine_amount,
        'fine_device': device_id,
        'fine_description': fine_description
    }

    if fine_type.name:
        if is_not_blank(fine_note):
            note_concatenation = f'{fine_type.name}: {fine_subtype.name}. BPI {device_id}. {fine_note}'
        else:
            note_concatenation = f'{fine_type.name}: {fine_subtype.name}. BPI {device_id}.'
    else:
        if is_not_blank(fine_note):
            note_concatenation = f'{fine_subtype.name}. BPI {device_id}. {fine_note}'
        else:
            note_concatenation = f'{fine_subtype.name}. BPI {device_id}.'

    note_concatenation = note_concatenation

    msb.post_student_invoice(str(user.id), fine_item)
    Note.objects.create(item_id = user.id, body = note_concatenation, author = request.user, attached_id = None)

    if user.iiq_id != None:
        iiq.prepend_user_notes(user.iiq_id, note_concatenation, request.user.username)
    else:
        try:
            iiq.get_user_uuid(user.id)
            iiq.prepend_user_notes(user.iiq_id, note_concatenation, request.user.username)
        except:
            pass

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff', 'IDOnly'])
@csrf_exempt
def add_id_print_log(request):
    print(request.POST)

    if request.POST.get('label_size') == 'large-label':
        student = StudentModel.objects.get(id = request.POST.get('student_id'))

        student_log = StudentModelIDLog(
            author = request.user,
            student = student
        )

        student_log.save()

        if student_log.pk:
            return JsonResponse({
                'code': 200,
                'message': 'Successfully created database entry.'
            })
        else:
            return JsonResponse({
                'code': 400,
                'message': 'Unable to create database entry.'
            })
    else:
        return JsonResponse({
            'code': 201,
            'message': 'Only the large labels are tracked in the database...'
        })

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def add_summer_program(request):
    student = StudentModel.objects.get(id = request.POST.get('student_id'))
    program = PersonPrograms.objects.get(id = request.POST.get('program_id'))
    user = User.objects.get(id = request.POST.get('user_id'))

    student.foreign_status_id = 'SP'
    student.save_without_historical_record()

    StudentModelPrograms.objects.create(student = student, created = timezone.now(), author = user, program = program)
    Note.objects.create(item_id = student.id, body = f"Summer program enrollment: {program.id}.", author = user)

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def add_device_submit(request):
    student = StudentModel.objects.get(id = request.POST.get('student_id'))
    device = Device.objects.get(id = request.POST.get('device_id'))
    note = request.POST.get('assign_note')
    author = request.user

    assign_device = device_utility.set_owner(device, student, request.user)
    assign_response = json.loads(assign_device.content)

    if assign_response['code'] == 200:
        assign_note = f"Device BPI {device.id} assigned to student. {note}"
        response_data = response_template

        add_note_to_user(request.user, student, assign_note)
        response_data.update({
            'code': assign_response['code'],
            'status': assign_response['status'],
            'data': assign_response['data']
        })
    else:
        response_data = response_template

        response_data.update({
            'code': assign_response['code'],
            'status': assign_response['status'],
            'data': assign_response['data']
        })

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def get_device(request):
    current_datetime = timezone.now()
    device = Device.objects.get(id = request.POST.get('device_id'))
    device_owner = StudentModel.objects.get(id = request.POST.get('owner_id'))
    user_email = request.POST.get('user_email')

    context = {
        # Django
        'request': request,
        # QuerySets
        'device': device,
        'owner': device_owner,
        # Variables
        'current_datetime': current_datetime,
        'user_email': user_email
    }

    html = render_to_string('users/detail_modifydevice_offcanvas.html', context, request = request)
    return HttpResponse(html)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def modify_device_submit(request):
    ownership = StudentDeviceOwnership.objects.get(device_id = request.POST.get('device_id'))
    device = Device.objects.get(id = ownership.device.id)
    device_name = device.foreign_model.name
    student = StudentModel.objects.get(id = ownership.student.id)

    try:
        distributions = DataDistribution.objects.get(student_id = student.id)
    except:
        distributions = False

    damage_present = not bool(strtobool(request.POST.get('device_damage_present')))
    student_email = f"{student.username}@flaglercps.org"

    school_year_start = constance_config.current_school_year_start
    school_year_end = constance_config.current_school_year_end

    assessment_object = DeviceAssessment.objects.create(device = device, device_damage_present = damage_present, author = request.user)

    device_damage_dd = bool(strtobool(request.POST.get('device_damage_dd'))) if 'device_damage_dd' in request.POST else False
    device_damage_edd = bool(strtobool(request.POST.get('device_damage_edd'))) if 'device_damage_edd' in request.POST else False
    device_damage_lis = bool(strtobool(request.POST.get('device_damage_lis'))) if 'device_damage_lis' in request.POST else False
    device_damage_cs = bool(strtobool(request.POST.get('device_damage_cs'))) if 'device_damage_cs' in request.POST else False
    device_damage_tnc = bool(strtobool(request.POST.get('device_damage_tnc'))) if 'device_damage_tnc' in request.POST else False
    device_damage_tc = bool(strtobool(request.POST.get('device_damage_tc'))) if 'device_damage_tc' in request.POST else False
    device_damage_prt = bool(strtobool(request.POST.get('device_damage_prt'))) if 'device_damage_prt' in request.POST else False
    device_damage_ms = bool(strtobool(request.POST.get('device_damage_ms'))) if 'device_damage_ms' in request.POST else False
    device_damage_ld = bool(strtobool(request.POST.get('device_damage_ld'))) if 'device_damage_ld' in request.POST else False
    device_damage_mkr = bool(strtobool(request.POST.get('device_damage_mkr'))) if 'device_damage_mkr' in request.POST else False
    device_damage_mku = bool(strtobool(request.POST.get('device_damage_mku'))) if 'device_damage_mku' in request.POST else False
    device_damage_bci = bool(strtobool(request.POST.get('device_damage_bci'))) if 'device_damage_bci' in request.POST else False
    device_damage_ccd = bool(strtobool(request.POST.get('device_damage_dd'))) if 'device_damage_dd' in request.POST else False

    if damage_present:
        assessment_object.device_damage_dd = device_damage_dd
        assessment_object.device_damage_edd = device_damage_edd
        assessment_object.device_damage_lis = device_damage_lis
        assessment_object.device_damage_cs = device_damage_cs
        assessment_object.device_damage_tnc = device_damage_tnc
        assessment_object.device_damage_tc = device_damage_tc
        assessment_object.device_damage_prt = device_damage_prt
        assessment_object.device_damage_ms = device_damage_ms
        assessment_object.device_damage_ld = device_damage_ld
        assessment_object.device_damage_mkr = device_damage_mkr
        assessment_object.device_damage_mku = device_damage_mku
        assessment_object.device_damage_bci = device_damage_bci
        assessment_object.device_damage_ccd = device_damage_ccd

    device_bin = request.POST.get('device_bin') if 'device_bin' in request.POST else None
    assessment_object.device_bin = device_bin

    assessment_object.save()

    finable_offenses = [assessment_object.device_damage_cs, assessment_object.device_damage_tc, assessment_object.device_damage_prt, assessment_object.device_damage_ld, assessment_object.device_damage_mku]
    assessed_damages = {}

    if sum(finable_offenses) > 0:
        student_invoices = msb.get_invoices_by_student_id(student.id)

        student_invoice_ids = []
        student_invoice_details = {}

        if bool(student_invoices):
            for invoice in student_invoices:
                for key, value in invoice.items():
                    if key == 'invoiceID':
                        student_invoice_ids.append(value)

        for id in student_invoice_ids:
            invoice_detail = msb.get_invoice_by_invoice_id(id)

            for fee in invoice_detail[0]['invoiceItems']:
                student_invoice_details.update({
                    str(uuid.uuid4()): {
                        'date': fee['createdDate'],
                        'description': fee['desc']
                    }
                })

        fine_level = 0

        for value in student_invoice_details.values():
            date_raw = datetime.datetime.strptime(value['date'].replace('T', ' ')[0:-5], '%Y-%m-%d %H:%M:%S')
            date = datetime.date(date_raw.year, date_raw.month, date_raw.day)
            description = value['description']
            ordinals = ['1st', '2nd', '3rd', '4th']

            if date >= school_year_start and date <= school_year_end:
                if device_name.split(' ')[0] in description and any(ordinal in description for ordinal in ordinals):
                    fine_level += 1

        if assessment_object.device_damage_cs:
            if fine_level > 3:
                fine_level = 3
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "CS")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name.split(' ')[0]} {device_name.split(' ')[1]} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

        if assessment_object.device_damage_tc:
            if fine_level > 3:
                fine_level = 3
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "TD")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name.split(' ')[0]} {device_name.split(' ')[1]} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

        if assessment_object.device_damage_prt:
            if fine_level > 3:
                fine_level = 3
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "PRT")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name.split(' ')[0]} {device_name.split(' ')[1]} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

        if assessment_object.device_damage_ld:
            if fine_level > 3:
                fine_level = 3
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "LD")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name.split(' ')[0]} {device_name.split(' ')[1]} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

        if assessment_object.device_damage_mku:
            if fine_level > 3:
                fine_level = 3
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "MKU")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name.split(' ')[0]} {device_name.split(' ')[1]} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

    if is_blank(device.iiq_id):
        device.set_iiq_id()

        asset_uuid = device.iiq_id
    else:
        asset_uuid = device.iiq_id

    if is_blank(str(student.iiq_id)):
        owner_uuid = iiq.get_user_uuid(student.id)
        student.iiq_id = owner_uuid

        student.save_without_historical_record()
    else:
        owner_uuid = student.iiq_id

    if len(assessed_damages) > 0:
        msb.post_student_invoice_multiple(student.id, assessed_damages)

        device_ticket = iiq.create_device_checkin_ticket(str(student.location.id))
        ticket_description = f"Student Information\n\nStudent ID: {student.id}\nDevice BPI: {device.id}\n\nStudent Name: {student.name}\nStudent Username: {student.username}\nStudent Grade: {student.grade}\n\nDamages\n\n"

        for damage in assessed_damages.values():
            ticket_description += f"{damage['fine_description']}: {damage['fine_subtype']}\n"

        iiq.assign_ticket_device(device_ticket['ticket_id'], device_ticket['ticket_asset_id'], device.iiq_id)
        iiq.assign_ticket_agent_and_team(device_ticket['ticket_id'], device_ticket['agent_uuid'], device_ticket['team_uuid'])
        iiq.change_ticket_description_and_location(device_ticket['ticket_id'], device_ticket['location_uuid'], ticket_description)
        iiq.change_ticket_owner_and_user(device_ticket['ticket_id'], device_ticket['agent_uuid'], owner_uuid)

    if request.POST.get('device_submit_type') == 'checkin':
        device_utility.remove_owner(device, request.user, {'device_bpi': device.id, 'device_bin': request.POST.get('device_bin')})

        device.bin = request.POST.get('device_bin')
        device.save_without_historical_record()

        if student.status_id == 'A' or student.status_id == 'SP':
            try:
                distribution_data = DataDistribution.objects.get(student_id = student.id)
            except:
                distribution_data = None

            if distribution_data != None:
                if distribution_data.updated.date() >= constance_config.dlmr_year_start:
                    distribution_date = '22-23'
                elif datetime.date(2021, 5, 8) < distribution_data.updated.date() < constance_config.dlmr_year_start:
                    distribution_date = '21-22'
                else:
                    distribution_date = None

                if distribution_date == '21-22':
                    archive_dlmr_record(distribution_data)

    assessment_note = f"Device BPI {device.id} {'checked in' if request.POST.get('device_submit_type') == 'checkin' else 'modified'}: {request.POST.get('device_note')}"

    Note.objects.create(item_id = student.id, body = assessment_note, author = request.user)

    if request.POST.get('send_checkin_receipt') == 'true':
        email_context = {
            'current_school_year': f"{constance_config.current_school_year_start.year}-{constance_config.current_school_year_end.year}",
            'device_assessment_message': f"{device.foreign_model.name.split(' ')[0]} checked in. Damage present: ",
            'device_bpi': device.id,
            'device_model': device.foreign_model.name,
            'student_address': distributions.parent_address if distributions else student_email,
            'student_name': student.name
        }

        if len(assessed_damages) > 0:
            for damage in assessed_damages.values():
                email_context['device_assessment_message'] += f"{damage['fine_description']}, {damage['fine_subtype']}. "
        else:
            email_context['device_assessment_message'] += "none."

        if len(request.POST.get('additional_emails')) > 0:
            queue_html_email(recipient=student_email, subject='Device Return Receipt', template='users/detail_modifydevice_email.html', context=email_context, cc_recipients=request.POST.get('additional_emails'))
        else:
            queue_html_email(recipient=student_email, subject='Device Return Receipt', template='users/detail_modifydevice_email.html', context=email_context)

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def add_charger_submit(request):
    user = StudentModel.objects.get(id = request.POST.get('student_id'))
    charger_type = ChargerType.objects.get(id = request.POST.get('charger_type'))
    author = request.user

    try:
        charger_exists = Charger.objects.filter(id = StudentChargerOwnership.objects.filter(charger__type = charger_type, charger__location = Location.objects.get(id = user.location.id), student_id__isnull = True).first().charger_id).exists()
    except:
        charger_exists = False

    if charger_exists:
        existing_charger = Charger.objects.get(id = StudentChargerOwnership.objects.filter(charger__type = charger_type, charger__location = Location.objects.get(id = user.location.id), student_id__isnull = True).first().charger_id)
    else:
        existing_charger = None

    if existing_charger != None:
        charger_utility.set_owner(existing_charger, user, request.user)
    else:
        created_charger = Charger.objects.create(
            type = charger_type,
            status = ChargerCondition.objects.get(id = request.POST.get('charger_condition')),
            location = Location.objects.get(id = user.location.id)
        )

        created_charger.save()

        charger_utility.set_owner(created_charger, user, request.user)

    note_concatenation = f'Peripheral Added: {charger_type.name}. {request.POST.get("charger_note")}'

    Note.objects.create(item_id = user.id, body = note_concatenation, author = request.user, attached_id = None)

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def get_charger(request):
    current_datetime = timezone.now()
    charger = Charger.objects.get(id = request.POST.get('charger_id'))
    ownership = StudentChargerOwnership.objects.get(charger_id = charger.id)
    charger_condition = ChargerCondition.objects.all()

    context = {
        # Django
        'request': request,
        # QuerySets
        'charger': charger,
        'charger_condition': charger_condition,
        'ownership': ownership,
        # Variables
        'current_datetime': current_datetime
    }

    html = render_to_string('users/detail_modifycharger_offcanvas.html', context, request = request)

    return HttpResponse(html)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def modify_charger_submit(request):
    charger = Charger.objects.get(id = request.POST.get('charger_id'))
    ownership = StudentChargerOwnership.objects.get(charger_id = charger.id)
    author = request.user

    if 'charger_damage_br' in request.POST:
        charger_damage_br = bool(strtobool(request.POST.get('charger_damage_br')))
    else:
        charger_damage_br = False

    if 'charger_damage_co' in request.POST:
        charger_damage_co = bool(strtobool(request.POST.get('charger_damage_co')))
    else:
        charger_damage_co = False

    if 'charger_damage_ms2' in request.POST:
        charger_damage_ms2 = bool(strtobool(request.POST.get('charger_damage_ms2')))
    else:
        charger_damage_ms2 = False

    if 'charger_damage_case' in request.POST:
        charger_damage_case = bool(strtobool(request.POST.get('charger_damage_case')))
    else:
        charger_damage_case = False

    print(charger_damage_case)

    if 'charger_add_br' in request.POST:
        charger_add_br = bool(strtobool(request.POST.get('charger_add_br')))
    else:
        charger_add_br = False

    if 'charger_add_co' in request.POST:
        charger_add_co = bool(strtobool(request.POST.get('charger_add_co')))
    else:
        charger_add_co = False

    if (charger_damage_br or charger_damage_co) and not charger_damage_ms2:
        if charger_damage_br and charger_damage_co:
            fine_items = {}

            fine_items.update({
                1: {
                    'fine_type': "Standard Fine",
                    'fine_subtype': charger.type.combined_fine.name,
                    'fine_amount': charger.type.combined_fine.value,
                    'fine_device': 'N/A',
                    'fine_description': charger.type.combined_fine.description
                }
            })

            note_concatenation = f'Standard Fine: {charger.type.combined_fine.description} BPI N/A. {request.POST.get("charger_note")}'

            try:
                msb.post_student_invoice_multiple(ownership.student.id, fine_items)
            except:
                HttpResponse("Something went wrong communicating with MySchoolBucks and changes have not been saved. Please try again or contact your school's IT support technician(s) to troubleshoot the issue further.")

            Note.objects.create(item_id = ownership.student.id, body = note_concatenation, author = author, attached_id = None)
            charger.modify_parts(not charger_damage_br, not charger_damage_co)
        else:
            fine_items = {}
            count = 1

            if charger_damage_br:
                fine_items.update({
                    count: {
                        'fine_type': "Standard Fine",
                        'fine_subtype': charger.type.brick_fine.name,
                        'fine_amount': charger.type.brick_fine.value,
                        'fine_device': 'N/A',
                        'fine_description': charger.type.brick_fine.description
                    }
                })

                count += 1
                note_concatenation = f'Standard Fine: {charger.type.brick_fine.description} BPI N/A. {request.POST.get("charger_note")}'

            if charger_damage_co:
                fine_items.update({
                    count: {
                        'fine_type': "Standard Fine",
                        'fine_subtype': charger.type.cable_fine.name,
                        'fine_amount': charger.type.cable_fine.value,
                        'fine_device': 'N/A',
                        'fine_description': charger.type.cable_fine.description
                    }
                })

                note_concatenation = f'Standard Fine: {charger.type.cable_fine.description} BPI N/A. {request.POST.get("charger_note")}'

            try:
                msb.post_student_invoice_multiple(ownership.student.id, fine_items)
            except:
                HttpResponse("Something went wrong communicating with MySchoolBucks and changes have not been saved. Please try again or contact your school's IT support technician(s) to troubleshoot the issue further.")

            Note.objects.create(item_id = ownership.student.id, body = note_concatenation, author = author, attached_id = None)
            charger.modify_parts(not charger_damage_br, not charger_damage_co)
    elif charger_damage_ms2 or charger_damage_case and (not charger_damage_br or not charger_damage_co):
        fine_items = {}

        fine_items.update({
            1: {
                'fine_type': "Standard Fine",
                'fine_subtype': charger.type.combined_fine.name,
                'fine_amount': charger.type.combined_fine.value,
                'fine_device': 'N/A',
                'fine_description': charger.type.combined_fine.description
            }
        })

        print(fine_items)

        note_concatenation = f'Standard Fine: {charger.type.combined_fine.description} BPI N/A. {request.POST.get("charger_note")}'

        try:
            msb.post_student_invoice_multiple(ownership.student.id, fine_items)
        except:
            HttpResponse("Something went wrong communicating with MySchoolBucks and changes have not been saved. Please try again or contact your school's IT support technician(s) to troubleshoot the issue further.")

        Note.objects.create(item_id = ownership.student.id, body = note_concatenation, author = author, attached_id = None)
        charger.modify_parts(not charger_damage_br, not charger_damage_co)

    if (not charger_damage_br and not charger_damage_co) and not charger_damage_ms2:
        note_concatenation = f'Charger Check-in: No Damage. {request.POST.get("charger_note")}'

        Note.objects.create(item_id = ownership.student.id, body = note_concatenation, author = author, attached_id = None)

    if charger_add_br or charger_add_co:
        if charger_add_br and not charger_add_co:
            charger.modify_parts(charger_add_br, not charger_add_co)
        elif not charger_add_br and charger_add_co:
            charger.modify_parts(not charger_add_br, charger_add_co)
        elif charger_add_br and charger_add_co:
            charger.modify_parts(charger_add_br, charger_add_co)

        if charger_add_br and not charger_add_co:
            if charger.type.brick_fine:
                part_note = charger.type.brick_fine.name
            else:
                part_note = charger.type.name
        elif not charger_add_br and charger_add_co:
            if charger.type.cable_file:
                part_note = charger.type.cable_fine.name
            else:
                part_note = charger.type.name
        elif charger_add_br and charger_add_co:
            if charger.type.combined_fine:
                part_note = charger.type.combined_fine.name
            else:
                part_note = charger.type.name
        else:
            part_note = 'Unknown'

        note_concatenation = f'Charger Part(s) Added: {part_note}. {request.POST.get("charger_note")}'

        Note.objects.create(item_id = ownership.student.id, body = note_concatenation, author = author, attached_id = None)

    if charger_damage_ms2 or (charger_damage_br and charger_damage_co):
        charger.status = ChargerCondition.objects.get(id = 'D')
        charger_utility.remove_owner(charger, author)

    if request.POST.get("charger_submit_type") == "checkin":
        if ownership.student != None:
            charger_utility.remove_owner(charger, author)

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def update_student_password(request):
    user = StudentModel.objects.get(id = request.POST.get('student_id'))
    password = request.POST.get('new_password')

    if is_not_blank(password):
        user.password = password
        user.save()

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def update_staging_data(request):
    response_data = {}

    try:
        staging_data = DataStaging.objects.get(student_id = request.POST.get('student_id'))
        staging_data.device_bin = request.POST.get('device_bin')
        staging_data.device_bpi = request.POST.get('device_bpi')

        staging_data.save()
    except:
        print(f"No existing Staging Data found for user {request.POST.get('student_id')}.")
        DataStaging.objects.create(student_id = request.POST.get('student_id'), device_bpi = request.POST.get('device_bpi'), device_bin = request.POST.get('device_bin'))

    try:
        device = Device.objects.get(id = staging_data.device_bpi)
        device.bin = staging_data.device_bin

        device.save()
    except:
        pass

    response_data['response'] = True
    return JsonResponse(response_data)

def collect_device(request):
    from users.models import StudentDeviceOwnership

    record = StudentDeviceOwnership.objects.get(id = request.POST.get('record_id'))

    grades = sadis_config.COLLECTIONS_GRADE_LEVELS
    locations = Location.objects.filter(id__in = sadis_config.SIDELOAD_LOCATIONS)
    current_datetime = datetime.datetime.now()

    if DataDistribution.objects.filter(student_id = record.student.id).exists():
        user_data = DataDistribution.objects.get(student_id = record.student.id)
    else:
        user_data = None

    context = {
        # Django
        'request': request,
        # QuerySets
        'record': record,
        'user_data': user_data,
        # Variables
        'grades': grades,
        'locations': locations,
        'current_datetime': current_datetime
    }

    html = render_to_string('users/collections_modal.html', context, request = request)
    return HttpResponse(html)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def collect_device_submit(request):
    from users.models import StudentDeviceOwnership, StudentChargerOwnership, NewDataCollection

    current_datetime = timezone.now()
    school_year_start = constance_config.current_school_year_start
    school_year_end = constance_config.current_school_year_end

    # Record Information
    record_id = request.POST.get('record_id')
    record = StudentDeviceOwnership.objects.get(id = record_id)

    # Student Information
    student_id = record.student.id
    student = StudentModel.objects.get(id = student_id)

    try:
        student_distributions = DataDistribution.objects.get(student_id = student.id)
    except:
        student_distributions = None

    student_next_location = None
    if 'student_next_school' in request.POST and is_not_blank(request.POST.get('student_next_school')):
        student_next_location = request.POST.get('student_next_school')

    student_next_grade = None
    if 'student_next_grade' in request.POST and is_not_blank(request.POST.get('student_next_grade')):
        student_next_grade = request.POST.get('student_next_grade')

    # If IIQ is active in constance...
    if constance_config.iiq_enabled:
        if is_blank(str(student.iiq_id)):
            owner_uuid = iiq.get_user_uuid(student.id)
            student.iiq_id = owner_uuid

            student.save_without_historical_record()
        else:
            owner_uuid = student.iiq_id

    # Parent Information
    parent_name = 'John Doe'
    parent_address = '123 Doe Drive'
    parent_phone = '9999999999'
    parent_email = 'john@doe.com'

    # Device Information
    device_id = record.device.id
    device = Device.objects.get(id = device_id)
    device_return_type = request.POST.get('device_return_type')
    device_name = device.foreign_model.name
    device_damage_present = not bool(strtobool(request.POST.get('device_damage_present')))

    device_damage_dd = bool(strtobool(request.POST.get('device_damage_dd'))) if 'device_damage_dd' in request.POST else False
    device_damage_edd = bool(strtobool(request.POST.get('device_damage_edd'))) if 'device_damage_edd' in request.POST else False
    device_damage_lis = bool(strtobool(request.POST.get('device_damage_lis'))) if 'device_damage_lis' in request.POST else False
    device_damage_cs = bool(strtobool(request.POST.get('device_damage_cs'))) if 'device_damage_cs' in request.POST else False
    device_damage_tnc = bool(strtobool(request.POST.get('device_damage_tnc'))) if 'device_damage_tnc' in request.POST else False
    device_damage_tc = bool(strtobool(request.POST.get('device_damage_tc'))) if 'device_damage_tc' in request.POST else False
    device_damage_ms = bool(strtobool(request.POST.get('device_damage_ms'))) if 'device_damage_ms' in request.POST else False
    device_damage_ld = bool(strtobool(request.POST.get('device_damage_ld'))) if 'device_damage_ld' in request.POST else False
    device_damage_mkr = bool(strtobool(request.POST.get('device_damage_mkr'))) if 'device_damage_mkr' in request.POST else False
    device_damage_mku = bool(strtobool(request.POST.get('device_damage_mku'))) if 'device_damage_mku' in request.POST else False
    device_damage_bci = bool(strtobool(request.POST.get('device_damage_bci'))) if 'device_damage_bci' in request.POST else False
    device_damage_ccd = bool(strtobool(request.POST.get('device_damage_dd'))) if 'device_damage_dd' in request.POST else False
    device_damage_hd = bool(strtobool(request.POST.get('device_damage_hd'))) if 'device_damage_hd' in request.POST else False

    # Create a collections entry based on the most minimalistic information required; all boolean values default to False
    collections_object = NewDataCollection.objects.create(
        device = Device.objects.get(id = device_id),
        student = StudentModel.objects.get(id = student_id),
        author = request.user,
        student_next_location = Location.objects.get(id = student_next_location),
        student_next_grade = student_next_grade,
        device_return_type = device_return_type,
        device_damage_present = device_damage_present,
        parent_name = parent_name,
        parent_address = parent_address,
        parent_phone = parent_phone,
        parent_email = parent_email,
        device_bin = request.POST.get('device_bin')
    )

    # If there's any kind of damage present, grab all the values submitted by the agent and set it to the collections object accordingly
    if device_damage_present:
        collections_object.device_damage_dd = device_damage_dd
        collections_object.device_damage_edd = device_damage_edd
        collections_object.device_damage_lis = device_damage_lis
        collections_object.device_damage_cs = device_damage_cs
        collections_object.device_damage_tnc = device_damage_tnc
        collections_object.device_damage_tc = device_damage_tc
        collections_object.device_damage_ms = device_damage_ms
        collections_object.device_damage_ld = device_damage_ld
        collections_object.device_damage_mkr = device_damage_mkr
        collections_object.device_damage_mku = device_damage_mku
        collections_object.device_damage_bci = device_damage_bci
        collections_object.device_damage_ccd = device_damage_ccd

    # Get submitted charger information
    chargers = StudentChargerOwnership.objects.filter(student_id = student.id)
    charger_return_type = request.POST.get('charger_return_type')
    charger_damage_present = False if (charger_return_type == 'CNRSR' or charger_return_type == 'CNR') else not bool(strtobool(request.POST.get('charger_damage_present')))
    charger_damage_returned = bool(strtobool(request.POST.get('charger_damage_returned'))) if 'charger_damage_returned' in request.POST else False

    charger_damage_co = bool(strtobool(request.POST.get('charger_damage_co'))) if 'charger_damage_co' in request.POST else False
    charger_damage_br = bool(strtobool(request.POST.get('charger_damage_br'))) if 'charger_damage_br' in request.POST else False
    charger_damage_ms2 = bool(strtobool(request.POST.get('charger_damage_ms2'))) if 'charger_damage_ms2' in request.POST else False
    charger_damage_cm = bool(strtobool(request.POST.get('charger_damage_cm'))) if 'charger_damage_cm' in request.POST else False
    charger_damage_cd = bool(strtobool(request.POST.get('charger_damage_cd'))) if 'charger_damage_cd' in request.POST else False

    collections_object.charger_return_type = charger_return_type
    collections_object.charger_damage_present = charger_damage_present

    # If damage is present and it's a MagSafe, set damage to cord and brick to True...
    if charger_damage_ms2:
        collections_object.charger_damage_co = 1
        collections_object.charger_damage_br = 1
    else:
        # ... but if it's not a MagSafe, set the damage to the cord and brick according to whatever the tech submitted
        collections_object.charger_damage_co = charger_damage_co
        collections_object.charger_damage_br = charger_damage_br

    # Get bin information and save collections object
    collections_object.device_bin = request.POST.get('device_bin')
    collections_object.save()

    if constance_config.iiq_enabled:
        if is_blank(device.iiq_id):
            device.set_iiq_id()

    ## --  FINE INFORMATION

    # Find out how many fines that are billable that the agent reported on the collections form and declare and empty variable to track these assessments
    finable_offenses = [collections_object.device_damage_cs, collections_object.device_damage_tc, collections_object.device_damage_ld, collections_object.device_damage_mku]
    assessed_damages = {}

    # Since finable offenses are stored as numerical boolean values, if the sum is greater than zero there is a fine that needs to be processed
    if sum(finable_offenses) > 0:
        # Get all invoices assigned to a student in MySchoolBucks
        student_invoices = msb.get_invoices_by_student_id(student.id)

        # Create two empty lists (arrays) that'll hold all the information retrieved from MySchoolBucks about pre-existing fines
        student_invoice_ids = []
        student_invoice_details = {}

        # If the MySchoolBucks query isn't empty...
        if bool(student_invoices):
            # Loop through all the items SADIS retrieved...
            for invoice in student_invoices:
                # And place the invoice ID into the `student_invoice_ids` list
                for key, value in invoice.items():
                    if key == 'invoiceID':
                        student_invoice_ids.append(value)

        # For every ID collected by the MySchoolBucks query...
        for id in student_invoice_ids:
            # Query for the invoice's details...
            invoice_detail = msb.get_invoice_by_invoice_id(id)

            for fee in invoice_detail[0]['invoiceItems']:
                # And place the date they were assessed and what type of assessment it was into `student_invoice_details`, keyed with a random UUID
                student_invoice_details.update({
                    str(uuid.uuid4()): {
                        'date': fee['createdDate'],
                        'description': fee['desc']
                    }
                })

        # Initiate a fine severity tracker
        fine_level = 0

        for value in student_invoice_details.values():
            # Convert MySchoolBucks datetime object into a Python datetime object
            date_raw = datetime.datetime.strptime(value['date'].replace('T', ' ')[0:-5], '%Y-%m-%d %H:%M:%S')
            # Convert the datetime object into a date object
            date = datetime.date(date_raw.year, date_raw.month, date_raw.day)
            # Get the fine's description
            description = value['description']
            # Set up an ordinal list for what fines we're looking for
            ordinals = ['1st', '2nd', '3rd', '4th']

            # If the date for the fine in MySchoolBucks is in between this year's start and end dates...
            if date >= school_year_start and date <= school_year_end:
                # ... and the fine's description includes an ordinal in the ordinal list above...
                if device_name.split(' ')[0] in description and any(ordinal in description for ordinal in ordinals):
                    # ... advance the severity tracker so we know where to start when we assign a new fine
                    fine_level += 1

        # Check and see if there was a cracked screen...
        if collections_object.device_damage_cs:
            #... and if so, check the fine level; if it's over 4...
            if fine_level > 4:
                #... set the level to 4 (which is a duplicate of 3 for tracking purposes)
                fine_level = 4
            else:
                # Otherwise, just increment the severity level
                fine_level += 1

            # Get the fine type object for the current severity level
            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            # Get the fine subtype object for the fine subtype (ie. cracked screen, damaged trackpad, etcetera)
            fine_subtype = FineSubtypes.objects.get(alias = "CS")

            # Update the `assessed_damages` dictionary with the relevant fine data
            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

        if collections_object.device_damage_tc:
            if fine_level > 4:
                fine_level = 4
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "TD")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

        if collections_object.device_damage_ld:
            if fine_level > 4:
                fine_level = 4
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "LD")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

        if collections_object.device_damage_mku:
            if fine_level > 4:
                fine_level = 4
            else:
                fine_level += 1

            fine_type = FineTypes.objects.get(name = f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident")
            fine_subtype = FineSubtypes.objects.get(alias = "MKU")

            assessed_damages.update({
                str(uuid.uuid4()): {
                    'fine_type': fine_type.name,
                    'fine_subtype': fine_subtype.name,
                    'fine_amount': fine_type.value if fine_type.value else FineSubtypes.objects.get(name = f"{device_name} Replacement").value,
                    'fine_device': device.id,
                    'fine_description': f"{device_name.split(' ')[0]} {make_ordinal(fine_level)} Incident"
                }
            })

    # The note that will be posted to the student's account
    note_body = f'Student Collections {constance_config.collections_date}: Device {device.id}, {device.foreign_model.name}, turned in'

    # If there is one or more damages present on the student's device...
    if len(assessed_damages) > 0:
        #... post those fines to MSB...
        msb.post_student_invoice_multiple(student.id, assessed_damages)

        #... create a ticket in IncidentIQ with the student and device information, as well as what damages are present
        if constance_config.iiq_enabled:
            device_ticket = iiq.create_device_checkin_ticket(str(student.location.id))
            ticket_description = f"Student Collections Event\n\nStudent ID: {student.id}\nDevice BPI: {device.id}\n\nStudent Name: {student.name}\nStudent Username: {student.username}\nStudent Grade: {student.grade}\n\nDamages\n\n"

        # Since there are damages on the device, append to the note string the damage indicator...
        note_body += ' with damages:'

        #... and for every damage value present, add the appropraite description of the damage to the note
        for damage in assessed_damages.values():
            if constance_config.iiq_enabled:
                ticket_description += f"{damage['fine_description']}: {damage['fine_subtype']}\n"

            note_body += f" {damage['fine_description']}."

        #... then, finally, post that information to the ticket and change the ticket's properties to match the agent and school
        if constance_config.iiq_enabled:
            iiq.assign_ticket_device(device_ticket['ticket_id'], device_ticket['ticket_asset_id'], device.iiq_id)
            iiq.change_ticket_description_and_location(device_ticket['ticket_id'], device_ticket['location_uuid'], ticket_description)
            iiq.assign_ticket_agent_and_team(device_ticket['ticket_id'], device_ticket['agent_uuid'], device_ticket['team_uuid'])
            iiq.change_ticket_owner_and_user(device_ticket['ticket_id'], device_ticket['agent_uuid'], owner_uuid)
    elif device_damage_hd:
        hotspot_damage = {
            str(uuid.uuid4()): {
                'fine_type': 'Standard Fine',
                'fine_subtype': 'Hotspot Damaged',
                'fine_amount': 55,
                'fine_device': f'{device.id}',
                'fine_description': 'Hotspot found damaged when device was returned during Collections period.'
            }
        }

        note_body += ' with damages.'

        msb.post_student_invoice_multiple(student.id, hotspot_damage)
    elif device_return_type == 'DNR':
        hotspot_damage = {
            str(uuid.uuid4()): {
                'fine_type': 'Standard Fine',
                'fine_subtype': 'Hotspot Damaged',
                'fine_amount': 55,
                'fine_device': f'{device.id}',
                'fine_description': 'Hotspot not returned during 2020-2021 collections period.'
            }
        }

        note_body = f'Student Collections {constance_config.collections_date}: Device {device.id}, {device.foreign_model.name}, not returned as required during the collections period.'

        msb.post_student_invoice_multiple(student.id, hotspot_damage)
    else:
        # But if there isn't any damages, close the note string...
        note_body += ' without damages.'

    if charger_return_type == 'CNRSR':
        note_body += ' Charger not returned: Student keeping for summer refresh.'

    #... and finally, create the note!
    add_note_to_user(request.user, student, note_body)

    # Set device bin and unassigned asset from user
    device.bin = request.POST.get('device_bin')
    device.save()

    device.delete_owner(request.user)
    record.delete()

    ## -- CHARGER LOGIC (Undocumented)
    if charger_return_type == 'CR' or charger_return_type == 'CNR':
        if 'MacBook' in device.foreign_model.name:
            # charger = chargers.filter(Q(charger__type__name__icontains = 'MagSafe') | Q(charger__type__name__icontains = 'USB-C')).first()
            if 'M1' in device.foreign_model.name:
                charger = chargers.filter(charger__type__name__icontains = 'USB-C').first()
            else:
                charger = chargers.filter(charger__type__name__icontains = 'MagSafe').first()
        elif 'iPad' in device.foreign_model.name:
            charger = chargers.filter(Q(charger__type__name__icontains = 'USB-A') | Q(charger__type__name__icontains = 'USB-C')).first()
        elif ('CoolPad' in device.foreign_model.name or 'DuraForce' in device.foreign_model.name) or ('E6' in device.foreign_model.name or 'Jetpack' in device.foreign_model.name) or ('Zone' in device.foreign_model.name or 'R850' in device.foreign_model.name):
            charger = chargers.filter(charger__type__name__icontains = 'USB-Micro').first()
        else:
            charger = chargers.first()
    else:
        charger = None

    if charger:
        if (charger_damage_br or charger_damage_co) and not charger_damage_ms2:
            fine_items = {}

            if charger_damage_br and charger_damage_co:
                fine_items.update({
                    str(uuid.uuid4()): {
                        'fine_type': "Standard Fine",
                        'fine_subtype': charger.charger.type.combined_fine.name,
                        'fine_amount': charger.charger.type.combined_fine.value,
                        'fine_device': 'N/A',
                        'fine_description': charger.charger.type.combined_fine.description
                    }
                })

                note_concatenation = f'Standard Fine: {charger.charger.type.combined_fine.description} BPI {device.id}. {request.POST.get("charger_note")}'

                if charger_damage_returned:
                    note_concatenation += f'. Since the charger or parts of the charger were damaged, they were returned to the student.'

                Note.objects.create(item_id = charger.student.id, body = note_concatenation, author = request.user, attached_id = None)
            else:
                if charger_damage_br:
                    fine_items.update({
                        str(uuid.uuid4()): {
                            'fine_type': "Standard Fine",
                            'fine_subtype': charger.charger.type.brick_fine.name,
                            'fine_amount': charger.charger.type.brick_fine.value,
                            'fine_device': 'N/A',
                            'fine_description': charger.charger.type.brick_fine.description
                        }
                    })

                    note_concatenation = f'Standard Fine: {charger.charger.type.brick_fine.description} BPI {device.id}. {request.POST.get("charger_note")}'

                    if charger_damage_returned:
                        note_concatenation += f'. Since the charger or parts of the charger were damaged, they were returned to the student.'

                    Note.objects.create(item_id = charger.student.id, body = note_concatenation, author = request.user, attached_id = None)

                if charger_damage_co:
                    fine_items.update({
                        str(uuid.uuid4()): {
                            'fine_type': "Standard Fine",
                            'fine_subtype': charger.charger.type.cable_fine.name,
                            'fine_amount': charger.charger.type.cable_fine.value,
                            'fine_device': 'N/A',
                            'fine_description': charger.charger.type.cable_fine.description
                        }
                    })

                    note_concatenation = f'Standard Fine: {charger.charger.type.cable_fine.description} BPI {device.id}. {request.POST.get("charger_note")}'

                    if charger_damage_returned:
                        note_concatenation += f'. Since the charger or parts of the charger were damaged, they were returned to the student.'

                    Note.objects.create(item_id = charger.student.id, body = note_concatenation, author = request.user, attached_id = None)

                if charger_damage_cm:
                    fine_items.update({
                        str(uuid.uuid4()): {
                            'fine_type': "Standard Fine",
                            'fine_subtype': charger.charger.type.combined_fine.name,
                            'fine_amount': charger.charger.type.combined_fine.value,
                            'fine_device': 'N/A',
                            'fine_description': charger.charger.type.combined_fine.description
                        }
                    })

                    note_concatenation = f'Standard Fine: {charger.charger.type.cable_fine.description} BPI {device.id}. {request.POST.get("charger_note")}'

                    if charger_damage_returned:
                        note_concatenation += f'. Since the charger or parts of the charger were damaged, they were returned to the student.'

                    Note.objects.create(item_id = charger.student.id, body = note_concatenation, author = request.user, attached_id = None)

                if charger_damage_cd:
                    fine_items.update({
                        str(uuid.uuid4()): {
                            'fine_type': "Standard Fine",
                            'fine_subtype': charger.charger.type.combined_fine.name,
                            'fine_amount': charger.charger.type.combined_fine.value,
                            'fine_device': 'N/A',
                            'fine_description': charger.charger.type.combined_fine.description
                        }
                    })

                    note_concatenation = f'Standard Fine: {charger.charger.type.cable_fine.description} BPI {device.id}. {request.POST.get("charger_note")}'

                    if charger_damage_returned:
                        note_concatenation += f'. Since the charger or parts of the charger were damaged, they were returned to the student.'

                    Note.objects.create(item_id = charger.student.id, body = note_concatenation, author = request.user, attached_id = None)
        elif charger_damage_ms2 and (not charger_damage_br or not charger_damage_co):
            fine_items = {}

            fine_items.update({
                str(uuid.uuid4()): {
                    'fine_type': "Standard Fine",
                    'fine_subtype': charger.charger.type.combined_fine.name,
                    'fine_amount': charger.charger.type.combined_fine.value,
                    'fine_device': 'N/A',
                    'fine_description': charger.charger.type.combined_fine.description
                }
            })

            note_concatenation = f'Standard Fine: {charger.charger.type.combined_fine.description} BPI N/A. {request.POST.get("charger_note")}'

            if charger_damage_returned:
                note_concatenation += f'. Since the charger or parts of the charger were damaged, they were returned to the student.'

            Note.objects.create(item_id = charger.student.id, body = note_concatenation, author = request.user, attached_id = None)
        else:
            fine_items = {}

        if charger_return_type == 'CR' and len(fine_items) == 0:
            Note.objects.create(item_id = charger.student.id, body = "Charger returned with device, no damages.", author = request.user, attached_id = None)

        if charger_return_type == 'CNR':
            if charger != None:
                fine_items.update({
                    str(uuid.uuid4()): {
                        'fine_type': "Standard Fine",
                        'fine_subtype': charger.charger.type.combined_fine.name,
                        'fine_amount': charger.charger.type.combined_fine.value,
                        'fine_device': 'N/A',
                        'fine_description': charger.charger.type.combined_fine.description
                    }
                })

                note_concatenation = f'Standard Fine: {charger.charger.type.combined_fine.description} BPI N/A.'

                if charger_damage_returned:
                    note_concatenation += f' Since the charger or parts of the charger were damaged, it was returned to the student.'

                Note.objects.create(item_id = charger.student.id, body = note_concatenation, author = request.user, attached_id = None)

        if len(fine_items) > 0:
            msb.post_student_invoice_multiple(charger.student.id, fine_items)

        charger.charger.modify_parts(not charger_damage_br, not charger_damage_co)
        charger.charger.delete_owner(request.user)
        charger.delete()

    ## -- EMAIL LOGIC
    student_email = f'{student.username}@flaglercps.org' if student.username else None

    email_context = {
        'current_school_year': f"{constance_config.current_school_year_start.year}-{constance_config.current_school_year_end.year}",
        'device_assessment_message': f"{device_name.split(' ')[0]} handed in for summer refresh. Damage present: ",
        'device_bpi': device.id,
        'device_model': device.foreign_model.name,
        'student_address': collections_object.parent_address,
        'student_name': student.name
    }

    if sum(finable_offenses) > 0:
        for damage in assessed_damages.values():
            email_context['device_assessment_message'] += f"{damage['fine_description']}, {damage['fine_subtype']}. "
    else:
        email_context['device_assessment_message'] += "None. "

    if charger_return_type != 'CR':
        email_context['device_assessment_message'] += "Issued power adapter not returned: student keeping over the summer."
    else:
        if len(fine_items) <= 0:
            email_context['device_assessment_message'] += "Issued power adapter returned with no damages."
        elif len(fine_items) > 0:
            email_context['device_assessment_message'] += "Issued power adapter returned with damages: "

            for value in fine_items.values():
                email_context['device_assessment_message'] += f"{value['fine_subtype']}. "

            if charger_damage_returned:
                email_context['device_assessment_message'] += f'Since the charger or parts of the charger were damaged, it was returned to the student.'

    queue_html_email(recipient = student_email, subject = 'Device Return Receipt', template = 'users/collections_email.html', context = email_context, cc_recipients = parent_email)

    ## -- ARCHIVE LOGIC

    # Check if there is a distributions record
    if student_distributions:
        archive_dlmr_record(student_distributions)

    # Change EC if they're not set to delinquint
    if student.role_id != 'DEL':
        if int(student.grade) > 3:
            student.role_id = 'OTO'
        else:
            student.role_id = 'ICVL'

        student.save()

    return JsonResponse(response_data)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def archive_dlmr_data(request):
    try:
        distributions_record = DataDistribution.objects.get(student_id = request.POST.get('student_id'))
    except:
        distributions_record = None

    if distributions_record != None:
        archive_dlmr_record(distributions_record)

    return JsonResponse({"code": 204, "message": "Request Successful"})
