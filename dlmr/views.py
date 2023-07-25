# Python
import datetime, re, json
from distutils.util import strtobool
# Django
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import View
# from django.core.serializers import json
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

# Plugins
from constance import config as constance_config
# SADIS
from inventory.models import Location, CalendlyAppointment
from inventory.utilities import get_query, queue_html_email
from users.models import DataDistribution, DataStaging, StudentModel, StudentDeviceOwnership, ContactValidation, EmergencyContactInfo, MedicalNeeds, SchoolClinicServices, MediaParentChoice

def dlm_registration(request):
    current_datetime = timezone.now()

    grades = ['KG', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    location_excludes = ['0000', '0061', '7005', '7006', '8000', '8001', '9999', 'N998']
    locations = Location.objects.exclude(id__in = location_excludes).order_by('name')

    context = {
        'grades': grades,
        'locations': locations,
        'calendly_enabled': constance_config.dlmr_calendar,
        'calendly_global_url': constance_config.dlmr_calendly_global,
        'calendly_tcd_url': constance_config.dlmr_calendly_tcd,
        'calendly_mhs_url': constance_config.dlmr_calendly_mhs,
        'calendly_fpc_url': constance_config.dlmr_calendly_fpc,
        'summer_only': constance_config.dlmr_summer_only
    }

    if request.method == 'POST':
        response_data = {}

        if request.POST.get('action') == 'get-student':
            students_query = StudentModel.objects.filter(get_query(f"{request.POST.get('student_first_name')} {request.POST.get('student_last_name')}", ['name']))

            student_location_id = request.POST.get('student_location_id')
            student_birthdate = datetime.datetime.strptime(f"{request.POST.get('student_birthdate')}", '%m/%d/%Y')

            try:
                student_result = students_query.get(birthdate = student_birthdate)
            except:
                student_result = None

            response = {}

            if student_result != None:
                device_result = StudentDeviceOwnership.objects.filter(Q(device__foreign_model__name__icontains = 'MacBook') | Q(device__foreign_model__name__icontains = 'iPad'), student_id = student_result.id, date__gte = constance_config.dlmr_year_start)

                if device_result.count() > 0:
                    response['student_has_device'] = 1
                else:
                    response['student_has_device'] = 0

                if constance_config.dlmr_calendar:
                    if (student_result.grade in ['KG', '01', '02', '03']) and (student_result.location_id != '7004'):
                        response['calendly_enabled'] = 0
                    else:
                        response['calendly_enabled'] = 1
                        cal = CalendlyAppointment.objects.filter(data__payload__questions_and_answers__0__answer = student_result.id)

                        if cal.count() >= 1:
                            appointment = cal.last()

                            if appointment['cancellation'] and not bool(strtobool(str(appointment['rescheduled']))):
                                response['calendly_appointment'] = 0
                            else:
                                response['calendly_appointment'] = 1
                        else:
                            response['calendly_appointment'] = 0
                else:
                    response['calendly_enabled'] = 0

                if constance_config.dlmr_calendar_secondary:
                    response['calendly_enabled_secondary'] = 1
                else:
                    response['calendly_enabled_secondary'] = 0

                if student_result.role_id != None:
                    response['student_ec'] = str(student_result.role_id).lower()
                else:
                    response['student_ec'] = None

                response['student_id'] = student_result.id
                response['student_name'] = student_result.name
                response['student_location'] = request.POST.get('student_location_id')
                response['student_grade'] = student_result.grade
                response['student_birthdate'] = request.POST.get('student_birthdate')
                response['student_status_id'] = student_result.status.id

                is_student_registered = DataDistribution.objects.filter(student_id = student_result.id).exists()

                if is_student_registered:
                    if DataDistribution.objects.get(student_id = student_result.id).created.date() < constance_config.dlmr_year_start:
                        response['student_not_collected'] = 1
                    else:
                        response['student_not_collected'] = 0
                else:
                    response['student_not_collected'] = 0

                if student_result.status.id == 'N':
                    response['student_is_new'] = 1
                else:
                    response['student_is_new'] = 0

                if student_result.status.id == 'SP' or student_result.status.id == 'EYR':
                    response['student_program'] = 1
                else:
                    response['student_program'] = 0

                if is_student_registered:
                    response['student_registered'] = 1
                else:
                    response['student_registered'] = 0

                if constance_config.dlmr_summer_only:
                    response['summer_program_only'] = 1
                else:
                    response['summer_program_only'] = 0

                response['response'] = 200
            else:
                response['response'] = 404

            return JsonResponse(response)

        if request.POST.get('action') == 'oto-form-submit':
            student_grade = request.POST.get('student_grade')
            student_id = request.POST.get('student_id')
            student_location_id = request.POST.get('student_location_id')
            student_name = request.POST.get('student_name')

            student_first_name = student_name.split(' ', 1)[0]
            student_last_name = student_name.split(' ', 1)[1]

            parent_address = request.POST.get('parent_address')
            parent_email = request.POST.get('parent_email')
            parent_name = request.POST.get('parent_name')
            parent_phone = request.POST.get('parent_phone')
            parent_signature = request.POST.get('parent_signature')
            media_choice_level = request.POST.get('media_choice_level')
            media_choice_electronic_signature = request.POST.get('media_choice_electronic_signature')
            clinic_services_electronic_signature = request.POST.get('clinic_services_electronic_signature')
            basic_first_aid = request.POST.get('basic_first_aid')
            minor_wound_care = request.POST.get('minor_wound_care')
            minor_eye_irritation = request.POST.get('minor_eye_irritation')
            minor_bites_and_stings = request.POST.get('minor_bites_and_stings')
            minor_upset_stomach = request.POST.get('minor_upset_stomach')
            check_for_rashes = request.POST.get('check_for_rashes')
            clinic_services_all = request.POST.get('clinic_services_all')
            fam_1_parent_1_name = request.POST.get('fam_1_parent_1_name')
            fam_1_parent_1_cell_phone = request.POST.get('fam_1_parent_1_cell_phone')
            fam_1_parent_1_daytime_phone = request.POST.get('fam_1_parent_1_daytime_phone')
            fam_1_parent_1_email = request.POST.get('fam_1_parent_1_email')
            fam_1_parent_2_name = request.POST.get('fam_1_parent_2_name')
            fam_1_parent_2_cell_phone = request.POST.get('fam_1_parent_2_cell_phone')
            fam_1_parent_2_daytime_phone = request.POST.get('fam_1_parent_2_daytime_phone')
            fam_1_parent_2_email = request.POST.get('fam_1_parent_2_email')
            fam_2_parent_1_name = request.POST.get('fam_2_parent_1_name')
            fam_2_parent_1_cell_phone = request.POST.get('fam_2_parent_1_cell_phone')
            fam_2_parent_1_daytime_phone = request.POST.get('fam_2_parent_1_daytime_phone')
            fam_2_email = request.POST.get('fam_2_email')
            fam_2_parent_2_name = request.POST.get('fam_2_parent_2_name')
            fam_2_parent_2_cell_phone = request.POST.get('fam_2_parent_2_cell_phone')
            fam_2_parent_2_daytime_phone = request.POST.get('fam_2_parent_2_daytime_phone')
            fam_1_residence = request.POST.get('fam_1_residence')
            fam_2_residence = request.POST.get('fam_2_residence')
            fam_1_mailing = request.POST.get('fam_1_mailing')
            fam_2_mailing = request.POST.get('fam_2_mailing')
            custody_paperwork = request.POST.get('custody_paperwork')
            allergies = request.POST.get('allergies')
            allergic_to = request.POST.get('allergic_to')
            glasses_or_contacts = request.POST.get('glasses_or_contacts')
            hearing_aids = request.POST.get('hearing_aids')
            physician_name = request.POST.get('physician_name')
            physician_phone = request.POST.get('physician_phone')




            promotion_code = request.POST.get('parent_promo')

            DataDistribution.objects.create(
                student_first_name = student_first_name,
                student_grade = student_grade,
                student_id = student_id,
                student_last_name = student_last_name,
                student_location_id = student_location_id,
                parent_address = parent_address,
                parent_agreement = 1,
                parent_email = parent_email,
                parent_name = parent_name,
                parent_phone = re.sub('[^0-9]', '', parent_phone),
                parent_signature = parent_signature,
                payment_amount = 0.00,
                payment_complete = 1,
                promotion_code = promotion_code
            )

            update_student = StudentModel.objects.get(id = student_id)
            update_student.role_id = 'OTO'
            update_student.save()

            email_context = {
                'student': update_student,
                'current_datetime': current_datetime.strftime('%m/%d/%Y'),
                'student_first_name': student_first_name,
                'student_grade': student_grade,
                'student_id': student_id,
                'student_last_name': student_last_name,
                'student_location': Location.objects.get(id = student_location_id).name,
                'parent_address': parent_address,
                'parent_email': parent_email,
                'parent_name': parent_name,
                'parent_phone': parent_phone,
                'parent_signature': parent_signature,
                'media_choice_level' : media_choice_level,
                'media_choice_electronic_signature' : media_choice_electronic_signature,
                'clinic_services_electronic_signature' : clinic_services_electronic_signature,
                'basic_first_aid': basic_first_aid,
                'minor_wound_care': minor_wound_care,
                'minor_eye_irritation': minor_eye_irritation,
                'minor_bites_and_stings': minor_bites_and_stings,
                'minor_upset_stomach': minor_upset_stomach,
                'check_for_rashes': check_for_rashes,
                'clinic_services_all': clinic_services_all,
                'fam_1_parent_1_name': fam_1_parent_1_name,
                'fam_1_parent_1_cell_phone': fam_1_parent_1_cell_phone,
                'fam_1_parent_1_daytime_phone': fam_1_parent_1_daytime_phone,
                'fam_1_parent_1_email': fam_1_parent_1_email,
                'fam_1_parent_2_name': fam_1_parent_2_name,
                'fam_1_parent_2_cell_phone': fam_1_parent_2_cell_phone,
                'fam_1_parent_2_daytime_phone': fam_1_parent_2_daytime_phone,
                'fam_1_parent_2_email': fam_1_parent_2_email,
                'fam_2_parent_1_name': fam_2_parent_1_name,
                'fam_2_parent_1_cell_phone': fam_2_parent_1_cell_phone,
                'fam_2_parent_1_daytime_phone': fam_2_parent_1_daytime_phone,
                'fam_2_email': fam_2_email,
                'fam_2_parent_2_name': fam_2_parent_2_name,
                'fam_2_parent_2_cell_phone': fam_2_parent_2_cell_phone,
                'fam_2_parent_2_daytime_phone': fam_2_parent_2_daytime_phone,
                'fam_1_residence': fam_1_residence,
                'fam_2_residence': fam_2_residence,
                'fam_1_mailing': fam_1_mailing,
                'fam_2_mailing': fam_2_mailing,
                'custody_paperwork': custody_paperwork,
                'allergies': allergies,
                'allergic_to': allergic_to,
                'glasses_or_contacts': glasses_or_contacts,
                'hearing_aids': hearing_aids,
                'physician_name': physician_name,
                'physician_phone': physician_phone,

            }

            try:
                device_bpi = DataStaging.objects.get(student_id = update_student.id).device_bpi
                device_bin = DataStaging.objects.get(student_id = update_student.id).device_bin

                email_context.update({
                    'bpi_bin': f'{device_bin}-{device_bpi}'
                })
            except:
                email_context.update({
                    'bpi_bin': None
                })

            queue_html_email(recipient = parent_email, subject = '23.24 1:1 DLM Registration Confirmation', template = 'dlmr/email.html', context = email_context)
            queue_html_email(recipient = parent_email, subject = '23.24 Form(s) Submission Confirmation', template = 'dlmr/email2.html', context = email_context)

            response_data['response'] = 200
            return JsonResponse(response_data)

        if request.POST.get('action') == 'du-form-submit':
            student_grade = request.POST.get('student_grade')
            student_id = request.POST.get('student_id')
            student_location_id = request.POST.get('student_location_id')
            student_name = request.POST.get('student_name')

            student_first_name = student_name.split(' ', 1)[0]
            student_last_name = student_name.split(' ', 1)[1]

            parent_address = request.POST.get('parent_address')
            parent_email = request.POST.get('parent_email')
            parent_name = request.POST.get('parent_name')
            parent_phone = request.POST.get('parent_phone')
            parent_signature = request.POST.get('parent_signature')
            media_choice_level = request.POST.get('media_choice_level')
            media_choice_electronic_signature = request.POST.get('media_choice_electronic_signature')
            clinic_services_electronic_signature = request.POST.get('clinic_services_electronic_signature')
            basic_first_aid = request.POST.get('basic_first_aid')
            minor_wound_care = request.POST.get('minor_wound_care')
            minor_eye_irritation = request.POST.get('minor_eye_irritation')
            minor_bites_and_stings = request.POST.get('minor_bites_and_stings')
            minor_upset_stomach = request.POST.get('minor_upset_stomach')
            check_for_rashes = request.POST.get('check_for_rashes')
            clinic_services_all = request.POST.get('clinic_services_all')
            fam_1_parent_1_name = request.POST.get('fam_1_parent_1_name')
            fam_1_parent_1_cell_phone = request.POST.get('fam_1_parent_1_cell_phone')
            fam_1_parent_1_daytime_phone = request.POST.get('fam_1_parent_1_daytime_phone')
            fam_1_parent_1_email = request.POST.get('fam_1_parent_1_email')
            fam_1_parent_2_name = request.POST.get('fam_1_parent_2_name')
            fam_1_parent_2_cell_phone = request.POST.get('fam_1_parent_2_cell_phone')
            fam_1_parent_2_daytime_phone = request.POST.get('fam_1_parent_2_daytime_phone')
            fam_1_parent_2_email = request.POST.get('fam_1_parent_2_email')
            fam_2_parent_1_name = request.POST.get('fam_2_parent_1_name')
            fam_2_parent_1_cell_phone = request.POST.get('fam_2_parent_1_cell_phone')
            fam_2_parent_1_daytime_phone = request.POST.get('fam_2_parent_1_daytime_phone')
            fam_2_email = request.POST.get('fam_2_email')
            fam_2_parent_2_name = request.POST.get('fam_2_parent_2_name')
            fam_2_parent_2_cell_phone = request.POST.get('fam_2_parent_2_cell_phone')
            fam_2_parent_2_daytime_phone = request.POST.get('fam_2_parent_2_daytime_phone')
            fam_1_residence = request.POST.get('fam_1_residence')
            fam_2_residence = request.POST.get('fam_2_residence')
            fam_1_mailing = request.POST.get('fam_1_mailing')
            fam_2_mailing = request.POST.get('fam_2_mailing')
            custody_paperwork = request.POST.get('custody_paperwork')
            allergies = request.POST.get('allergies')
            allergic_to = request.POST.get('allergic_to')
            glasses_or_contacts = request.POST.get('glasses_or_contacts')
            hearing_aids = request.POST.get('hearing_aids')
            physician_name = request.POST.get('physician_name')
            physician_phone = request.POST.get('physician_phone')


            promotion_code = request.POST.get('parent_promo')

            DataDistribution.objects.create(
                student_first_name = student_first_name,
                student_grade = student_grade,
                student_id = student_id,
                student_last_name = student_last_name,
                student_location_id = student_location_id,
                parent_address = parent_address,
                parent_agreement = 1,
                parent_email = parent_email,
                parent_name = parent_name,
                parent_phone = re.sub('[^0-9]', '', parent_phone),
                parent_signature = parent_signature,
                payment_amount = 0.00,
                payment_complete = 1,
                promotion_code = promotion_code
            )

            update_student = StudentModel.objects.get(id = student_id)
            update_student.role_id = 'DU'
            update_student.save()

            email_context = {
                'student': update_student,
                'current_datetime': current_datetime.strftime('%m/%d/%Y'),
                'student_first_name': student_first_name,
                'student_grade': student_grade,
                'student_id': student_id,
                'student_last_name': student_last_name,
                'student_location': Location.objects.get(id = student_location_id).name,
                'parent_address': parent_address,
                'parent_email': parent_email,
                'parent_name': parent_name,
                'parent_phone': parent_phone,
                'parent_signature': parent_signature,
                'media_choice_level' : media_choice_level,
                'media_choice_electronic_signature' : media_choice_electronic_signature,
                'clinic_services_electronic_signature' : clinic_services_electronic_signature,
                'basic_first_aid': basic_first_aid,
                'minor_wound_care': minor_wound_care,
                'minor_eye_irritation': minor_eye_irritation,
                'minor_bites_and_stings': minor_bites_and_stings,
                'minor_upset_stomach': minor_upset_stomach,
                'check_for_rashes': check_for_rashes,
                'clinic_services_all': clinic_services_all,
                'fam_1_parent_1_name': fam_1_parent_1_name,
                'fam_1_parent_1_cell_phone': fam_1_parent_1_cell_phone,
                'fam_1_parent_1_daytime_phone': fam_1_parent_1_daytime_phone,
                'fam_1_parent_1_email': fam_1_parent_1_email,
                'fam_1_parent_2_name': fam_1_parent_2_name,
                'fam_1_parent_2_cell_phone': fam_1_parent_2_cell_phone,
                'fam_1_parent_2_daytime_phone': fam_1_parent_2_daytime_phone,
                'fam_1_parent_2_email': fam_1_parent_2_email,
                'fam_2_parent_1_name': fam_2_parent_1_name,
                'fam_2_parent_1_cell_phone': fam_2_parent_1_cell_phone,
                'fam_2_parent_1_daytime_phone': fam_2_parent_1_daytime_phone,
                'fam_2_email': fam_2_email,
                'fam_2_parent_2_name': fam_2_parent_2_name,
                'fam_2_parent_2_cell_phone': fam_2_parent_2_cell_phone,
                'fam_2_parent_2_daytime_phone': fam_2_parent_2_daytime_phone,
                'fam_1_residence': fam_1_residence,
                'fam_2_residence': fam_2_residence,
                'fam_1_mailing': fam_1_mailing,
                'fam_2_mailing': fam_2_mailing,
                'custody_paperwork': custody_paperwork,
                'allergies': allergies,
                'allergic_to': allergic_to,
                'glasses_or_contacts': glasses_or_contacts,
                'hearing_aids': hearing_aids,
                'physician_name': physician_name,
                'physician_phone': physician_phone,
            }

            try:
                device_bpi = DataStaging.objects.get(student_id = update_student.id).device_bpi
                device_bin = DataStaging.objects.get(student_id = update_student.id).device_bin

                email_context.update({
                    'bpi_bin': f'{device_bin}-{device_bpi}'
                })
            except:
                email_context.update({
                    'bpi_bin': None
                })

            queue_html_email(recipient = parent_email, subject = '23.24 DU DLM Registration Confirmation', template = 'dlmr/email.html', context = email_context)
            queue_html_email(recipient = parent_email, subject = '23.24 Form(s) Submission Confirmation', template = 'dlmr/email2.html', context = email_context)

            response_data['response'] = 200
            return JsonResponse(response_data)

        if request.POST.get('action') == 'icvl-form-submit':
            student_grade = request.POST.get('student_grade')
            student_id = request.POST.get('student_id')
            student_location_id = request.POST.get('student_location_id')
            student_name = request.POST.get('student_name')

            student_first_name = student_name.split(' ', 1)[0]
            student_last_name = student_name.split(' ', 1)[1]

            parent_address = request.POST.get('parent_address')
            parent_email = request.POST.get('parent_email')
            parent_name = request.POST.get('parent_name')
            parent_phone = request.POST.get('parent_phone')
            parent_signature = request.POST.get('parent_signature')
            media_choice_level = request.POST.get('media_choice_level')
            media_choice_electronic_signature = request.POST.get('media_choice_electronic_signature')
            clinic_services_electronic_signature = request.POST.get('clinic_services_electronic_signature')
            basic_first_aid = request.POST.get('basic_first_aid')
            minor_wound_care = request.POST.get('minor_wound_care')
            minor_eye_irritation = request.POST.get('minor_eye_irritation')
            minor_bites_and_stings = request.POST.get('minor_bites_and_stings')
            minor_upset_stomach = request.POST.get('minor_upset_stomach')
            check_for_rashes = request.POST.get('check_for_rashes')
            clinic_services_all = request.POST.get('clinic_services_all')
            fam_1_parent_1_name = request.POST.get('fam_1_parent_1_name')
            fam_1_parent_1_cell_phone = request.POST.get('fam_1_parent_1_cell_phone')
            fam_1_parent_1_daytime_phone = request.POST.get('fam_1_parent_1_daytime_phone')
            fam_1_parent_1_email = request.POST.get('fam_1_parent_1_email')
            fam_1_parent_2_name = request.POST.get('fam_1_parent_2_name')
            fam_1_parent_2_cell_phone = request.POST.get('fam_1_parent_2_cell_phone')
            fam_1_parent_2_daytime_phone = request.POST.get('fam_1_parent_2_daytime_phone')
            fam_1_parent_2_email = request.POST.get('fam_1_parent_2_email')
            fam_2_parent_1_name = request.POST.get('fam_2_parent_1_name')
            fam_2_parent_1_cell_phone = request.POST.get('fam_2_parent_1_cell_phone')
            fam_2_parent_1_daytime_phone = request.POST.get('fam_2_parent_1_daytime_phone')
            fam_2_email = request.POST.get('fam_2_email')
            fam_2_parent_2_name = request.POST.get('fam_2_parent_2_name')
            fam_2_parent_2_cell_phone = request.POST.get('fam_2_parent_2_cell_phone')
            fam_2_parent_2_daytime_phone = request.POST.get('fam_2_parent_2_daytime_phone')
            fam_1_residence = request.POST.get('fam_1_residence')
            fam_2_residence = request.POST.get('fam_2_residence')
            fam_1_mailing = request.POST.get('fam_1_mailing')
            fam_2_mailing = request.POST.get('fam_2_mailing')
            custody_paperwork = request.POST.get('custody_paperwork')
            allergies = request.POST.get('allergies')
            allergic_to = request.POST.get('allergic_to')
            glasses_or_contacts = request.POST.get('glasses_or_contacts')
            hearing_aids = request.POST.get('hearing_aids')
            physician_name = request.POST.get('physician_name')
            physician_phone = request.POST.get('physician_phone')


            promotion_code = request.POST.get('parent_promo')

            DataDistribution.objects.create(
                student_first_name = student_first_name,
                student_grade = student_grade,
                student_id = student_id,
                student_last_name = student_last_name,
                student_location_id = student_location_id,
                parent_address = parent_address,
                parent_agreement = 1,
                parent_email = parent_email,
                parent_name = parent_name,
                parent_phone = re.sub('[^0-9]', '', parent_phone),
                parent_signature = parent_signature,
                payment_amount = 0.00,
                payment_complete = 1,
                promotion_code = promotion_code
            )

            update_student = StudentModel.objects.get(id = student_id)
            update_student.role_id = 'ICVL'
            update_student.save()

            email_context = {
                'student': update_student,
                'current_datetime': current_datetime.strftime('%m/%d/%Y'),
                'student_first_name': student_first_name,
                'student_grade': student_grade,
                'student_id': student_id,
                'student_last_name': student_last_name,
                'student_location': Location.objects.get(id = student_location_id).name,
                'parent_address': parent_address,
                'parent_email': parent_email,
                'parent_name': parent_name,
                'parent_phone': parent_phone,
                'parent_signature': parent_signature,
                'media_choice_level' : media_choice_level,
                'media_choice_electronic_signature' : media_choice_electronic_signature,
                'clinic_services_electronic_signature' : clinic_services_electronic_signature,
                'basic_first_aid': basic_first_aid,
                'minor_wound_care': minor_wound_care,
                'minor_eye_irritation': minor_eye_irritation,
                'minor_bites_and_stings': minor_bites_and_stings,
                'minor_upset_stomach': minor_upset_stomach,
                'check_for_rashes': check_for_rashes,
                'clinic_services_all': clinic_services_all,
                'fam_1_parent_1_name': fam_1_parent_1_name,
                'fam_1_parent_1_cell_phone': fam_1_parent_1_cell_phone,
                'fam_1_parent_1_daytime_phone': fam_1_parent_1_daytime_phone,
                'fam_1_parent_1_email': fam_1_parent_1_email,
                'fam_1_parent_2_name': fam_1_parent_2_name,
                'fam_1_parent_2_cell_phone': fam_1_parent_2_cell_phone,
                'fam_1_parent_2_daytime_phone': fam_1_parent_2_daytime_phone,
                'fam_1_parent_2_email': fam_1_parent_2_email,
                'fam_2_parent_1_name': fam_2_parent_1_name,
                'fam_2_parent_1_cell_phone': fam_2_parent_1_cell_phone,
                'fam_2_parent_1_daytime_phone': fam_2_parent_1_daytime_phone,
                'fam_2_email': fam_2_email,
                'fam_2_parent_2_name': fam_2_parent_2_name,
                'fam_2_parent_2_cell_phone': fam_2_parent_2_cell_phone,
                'fam_2_parent_2_daytime_phone': fam_2_parent_2_daytime_phone,
                'fam_1_residence': fam_1_residence,
                'fam_2_residence': fam_2_residence,
                'fam_1_mailing': fam_1_mailing,
                'fam_2_mailing': fam_2_mailing,
                'custody_paperwork': custody_paperwork,
                'allergies': allergies,
                'allergic_to': allergic_to,
                'glasses_or_contacts': glasses_or_contacts,
                'hearing_aids': hearing_aids,
                'physician_name': physician_name,
                'physician_phone': physician_phone,
            }

            try:
                device_bpi = DataStaging.objects.get(student_id = update_student.id).device_bpi
                device_bin = DataStaging.objects.get(student_id = update_student.id).device_bin

                email_context.update({
                    'bpi_bin': f'{device_bin}-{device_bpi}'
                })
            except:
                email_context.update({
                    'bpi_bin': None
                })

            queue_html_email(recipient = parent_email, subject = '23.24 ICVL DLM Registration Confirmation', template = 'dlmr/email.html', context = email_context)
            queue_html_email(recipient = parent_email, subject = '23.24 Form(s) Submission Confirmation', template = 'dlmr/email2.html', context = email_context)

            response_data['response'] = 200
            return JsonResponse(response_data)

    if constance_config.dlmr_closed:
        return render(request, 'dlmr/registration_closed.html', context)
    else:
        return render(request, 'dlmr/registration.html', context)

def dlm_registration_success(request):
    return render(request, 'dlmr/registration_success.html', {})

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