# Python
import json
from datetime import datetime
from distutils.util import strtobool
# Framework
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
# Modules
from constance import config as constance_config
# Application
from common.decorators import allowed_roles
from common.device import set_owner
from inventory.utilities import get_query, Qurl
from sadis.api import api_iiq as iiq
# Models
from inventory.models import Device, Note, Charger, ChargerCondition, ChargerType, Device
from modes.models import DistributionLane, DistributionQueue, DistributionStatus
from users.models import DataDistribution, DataStaging, StudentDeviceOwnership, StudentModel, StudentAppointments

@login_required(login_url = 'login')
@allowed_roles(['Administrator', 'Staff'])
def distributions(request):
    dlmr_year_start = timezone.make_aware(datetime.combine(constance_config.dlmr_year_start, datetime.min.time()))

    def get_distribution_data(student_id = None):
        if student_id != None:
            distribution_data = DataDistribution.objects.filter(student_id = student_id, updated__gte = dlmr_year_start)

            if distribution_data.count() > 0:
                if distribution_data.last().updated >= dlmr_year_start:
                    return ['23-24', True]
                elif distribution_data.last().updated < dlmr_year_start:
                    return ['22-23', False]
                else:
                    return [False, False]
            else:
                return [False, False]
        else:
            return [False, False]

    def get_staged_data(student_id = None):
        if student_id != None:
            staging_data = DataStaging.objects.filter(student_id = student_id, updated__gte = dlmr_year_start)

            if staging_data.count() > 0:
                return [staging_data.last().device_bin, staging_data.last().device_bpi]
            else:
                return False
        else:
            return False

    def get_assigned_chargers(student_id = None):
        if student_id != None:
            staging_data = DataStaging.objects.filter(student_id = student_id, updated__gte = dlmr_year_start)

            if staging_data.count() > 0:
                return [staging_data.last().device_bin, staging_data.last().device_bpi]
            else:
                return False
        else:
            return False

    def get_user_queue(requestor = request.user):
        try:
            return DistributionQueue.objects.filter(author = requestor, assigned__isnull = True)
        except:
            return None

    def get_user_lane(member = request.user):
        lane_membership = request.user.distributionlane_set.first()
        return lane_membership

    def is_device_in_queue(device_id = None):
        queue_object = DistributionQueue.objects.filter(bpi = device_id, assigned__isnull = True).count()

        if queue_object > 0:
            return True
        else:
            return False

    lane = get_user_lane()
    url = request.get_full_path()
    current_datetime = timezone.now()

    students = StudentModel.objects.all()
    queued_devices = get_user_queue().values_list('bpi_id', flat = True)

    if 'search' in request.GET and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['id', 'first_name', 'last_name', 'username'])
        search_results = students.filter(search_query).order_by('name')
        search_message = 'No results were found.'
    else:
        search_message = 'Please search for a student using the above search field.'
        search_results = None

    entries = {}
    appointments = {}

    if search_results != None:
        count = 1

        for student in search_results:
            devices_owned = StudentDeviceOwnership.objects.filter(student_id = student.id)
            chargers_owned = Charger.objects.filter(owner_id = student.id)

            staged_data = get_staged_data(student.id)
            distribution_data = get_distribution_data(student.id)
            appointment_data = StudentAppointments.objects.filter(student_id = student.id)

            entries.update({
                count: {
                    'student_id': student.id,
                    'student_uuid': student.iiq_id,
                    'student_name': f'{student.first_name} {student.last_name}',
                    'student_username': student.username,
                    'student_grade': student.get_grade(),
                    'student_location_id': student.location.id if student.location else None,
                    'student_location_name': student.location.name if student.location else None,
                    'student_ec': student.get_role_id(),
                    'devices_owned': [device.device.id for device in devices_owned] or None,
                    'chargers_owned': [charger.type.id for charger in chargers_owned] or None,
                    'completed_form': distribution_data[0],
                    'completed_payment': distribution_data[1],
                    'staged_bin': staged_data[0] if staged_data else None,
                    'staged_bpi': staged_data[1] if staged_data else None,
                    'appointment_time': appointment_data.latest('created').event.event_start if appointment_data else None
                }
            })

            count += 1

    print(entries)

    context = {
        # Queries
        'charger_conditions': ChargerCondition.objects.exclude(id__in = ['D', 'UW']),
        'charger_types': ChargerType.objects.all(),
        'queue_items': get_user_queue(),
        # Dictionaries
        'entries': entries,
        # Variables
        'current_datetime': current_datetime,
        'current_lane': lane,
        'queued_devices': queued_devices,
        'search_message': search_message
    }

    if request.method == 'POST':
        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

        if request.POST.get('action') == 'request-device':
            device_id = request.POST.get('device_id')

            if is_device_in_queue(device_id):
                return JsonResponse({"code": 400, "message": "The device you're requesting has already been added to a queue."})
            else:
                if Device.objects.filter(id = device_id, owner__isnull = True).count() == 1:
                    create_queue_item = DistributionQueue.objects.create(
                        student = StudentModel.objects.get(id = request.POST.get('student_id')),
                        author = request.user,
                        lane = DistributionLane.objects.get(name = lane),
                        bpi = Device.objects.get(id = device_id),
                        bin = request.POST.get('device_bin'),
                        status = DistributionStatus.objects.get(alias = 'R')
                    )
                else:
                    try:
                        device = Device.objects.get(id = device_id)

                        if device.owner_id != None:
                            return JsonResponse({"code": 401, "message": "You can't request this device: it's already assigned to a student."})
                        else:
                            return JsonResponse({"code": 402, "message": "You can't request this device: can't retrieve device from database."})
                    except:
                        return JsonResponse({"code": 404, "message": "You can't request this device: it isn't in the database."})

                return JsonResponse({"code": 200, "message": f"Successfully requested {create_queue_item.bpi}. Please track it in your queue."})

        if request.POST.get('action') == 'assign-device':
            response_data = {}
            asset_uuid = iiq.get_asset_uuid(request.POST.get('device_id'))

            the_student = StudentModel.objects.get(id = request.POST.get('student_id'))
            the_student_uuid = the_student.iiq_id

            modify_owner = Device.objects.get(id = request.POST.get('device_id'))
            entry = DistributionQueue.objects.get(id = request.POST.get('entry_id'))

            if modify_owner.owner_id == the_student.id:
                pass
            else:
                modify_owner.owner_id = the_student.id
                modify_owner.location_id = the_student.location_id
                modify_owner.owner_assign_date = timezone.now()
                modify_owner.owner_assign_author = request.user
                modify_owner.save()

                assign_device = set_owner(modify_owner, the_student, request.user)
                assign_response = json.loads(assign_device.content)

                if assign_response['code'] == 200:
                    assign_note = f"Device BPI {device.id} assigned to student during Distributions."
                    Note.objects.create(item_id = student.id, body = assign_note, author = request.user)

                entry.status = DistributionStatus.objects.get(alias = 'A')
                entry.assigned = timezone.now()
                entry.save()

            if bool(strtobool(request.POST.get('assign_charger'))):
                assign_charger_type = request.POST.get('assign_charger_type')
                assign_charger_condition = request.POST.get('assign_charger_condition')
                charger_owned = Charger.objects.filter(type_id = assign_charger_type, owner_id = the_student.id).exists()

                if not charger_owned:
                    charger_found = Charger.objects.filter(type_id = assign_charger_type, owner_id__isnull = True).last()

                    if charger_found != None:
                        charger_found.assign_owner(the_student, request.user)
                    else:
                        Charger.objects.create(
                            type = ChargerType.objects.get(id = assign_charger_type),
                            status = ChargerCondition.objects.get(id = assign_charger_condition),
                            owner = the_student,
                            location = the_student.location,
                            owner_assign_date = timezone.now(),
                            owner_assign_author = request.user
                        )

            response_data['assign_response'] = True

            return JsonResponse(response_data)
        elif request.POST.get('action') == 'remove-device':
            entry = DistributionQueue.objects.get(id = request.POST.get('entry_id'))
            entry_bpi = entry.bpi.id

            entry.delete()
            return JsonResponse({"code": 200, "message": f"Successfully removed {create_queue_item.bpi} from your queue."})
        elif request.POST.get('action') == 'new-device':
            ...

    return render(request, 'modes/distributions.html', context)

@login_required(login_url = 'login')
@allowed_roles(['Administrator', 'Staff'])
def distributions_runner(request):
    queue = DistributionQueue.objects.all()

    requested_queue = queue.filter(status = DistributionStatus.objects.get(alias = 'R'))
    requested_entries = {}
    requested_count = 1

    runner_queue = queue.filter(claimer_id = request.user.id).exclude(status__alias__in = ['A', 'P'])
    runner_entries = {}
    runner_count = 1

    for entry in requested_queue:
        chargers_owned = Charger.objects.filter(owner_id = entry.student.id)

        requested_entries.update({
            requested_count: {
                'entry_id': entry.id,
                'student_id': entry.student.id,
                'student_name': entry.student.name,
                'student_location_name': entry.student.location.name if entry.student.location else None,
                'chargers_owned': [charger.type.id for charger in chargers_owned] or None,
                'requested_lane': entry.lane.name,
                'requested_author': entry.author.get_full_name(),
                'requested_bpi': entry.bpi.id,
                'requested_bin': entry.bin
            }
        })

        requested_count += 1

    for entry in runner_queue:
        chargers_owned = Charger.objects.filter(owner_id = entry.student.id)

        runner_entries.update({
            runner_count: {
                'entry_id': entry.id,
                'entry_status': entry.status.alias,
                'student_name': entry.student.name,
                'chargers_owned': [charger.type.id for charger in chargers_owned] or None,
                'requestor_lane': entry.lane.name,
                'requestor_author': entry.author.get_full_name(),
                'requested_bpi': entry.bpi.id,
                'requested_bin': entry.bin
            }
        })

        runner_count += 1

    context = {
        # Dictionaries
        'requested_entries': requested_entries,
        'runner_entries': runner_entries
    }

    if request.method == 'POST':
        if request.POST.get('action') == 'claim-device':
            requested_entry = DistributionQueue.objects.get(id = request.POST.get('entry_id'))

            if requested_entry.claimer != None:
                return JsonResponse({"code": 400, "message": "The device you're trying to claim has already been claimed."})
            else:
                requested_entry.claimer = request.user
                requested_entry.claimed = timezone.now()
                requested_entry.status = DistributionStatus.objects.get(alias = 'C')

                requested_entry.save()
                return JsonResponse({"code": 200, "message": f"Successfully claimed {requested_entry.bpi.id}. Please track it in your queue."})

        if request.POST.get('action') == 'device-found':
            requested_entry = DistributionQueue.objects.get(id = request.POST.get('entry_id'))

            requested_entry.found = timezone.now()
            requested_entry.status = DistributionStatus.objects.get(alias = 'F')

            requested_entry.save()
            return JsonResponse({"code": 200, "message": f"Successfully reported {requested_entry.bpi.id} as found."})
        elif request.POST.get('action') == 'device-missing':
            requested_entry = DistributionQueue.objects.get(id = request.POST.get('entry_id'))

            requested_entry.found = timezone.now()
            requested_entry.status = DistributionStatus.objects.get(alias = 'NF')

            requested_entry.save()
            return JsonResponse({"code": 404, "message": f"Successfully reported {requested_entry.bpi.id} as not found."})

    return render(request, 'modes/distributions_runner.html', context)
