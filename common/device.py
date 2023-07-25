# Django
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
# Application
from sadis.api import api_iiq as iiq
from users.models import DataStaging, StudentDeviceOwnership

def set_iiq_id(device):
    device.iiq_id = iiq.get_asset_uuid(device.id)
    device.save()

def set_owner(device, user, author):
    if not device.iiq_id:
        set_iiq_id(device)

    if StudentDeviceOwnership.objects.filter(device_id = device.id).exists():
        record = StudentDeviceOwnership.objects.get(device_id = device.id)

        if record.student != None:
            return_response = {
                'code': 403,
                'status': 'fail',
                'data': {
                    'message': 'Device is currently assigned to another student.'
                }
            }

            return JsonResponse(return_response)
        else:
            record.author = author
            record.date = timezone.now()
            record.student = user

            record.save()

            try:
                staged_data = DataStaging.objects.get(student_id = record.student.id)
            except:
                staged_data = None

            if staged_data != None:
                staged_data.device_bpi = None
                staged_data.device_bin = None

                staged_data.save()

            return_response = {
                'code': 200,
                'status': 'success',
                'data': {
                    'message': 'Device was successfully assigned in SADIS.'
                }
            }

            if user.status_id != 'N':
                iiq.assign_asset_to_user_by_force(device.iiq_id, user.iiq_id)

                return_response['data'].update({
                    'message': 'Device was successfully assigned in SADIS and IIQ.'
                })


            return JsonResponse(return_response)
    else:
        record = StudentDeviceOwnership(
            author = author,
            device = device,
            student = user
        )

        record.save()

        try:
            staged_data = DataStaging.objects.get(student_id = record.student.id)
        except:
            staged_data = None

        if staged_data != None:
            staged_data.device_bpi = None
            staged_data.device_bin = None

            staged_data.save()

        return_response = {
            'code': 200,
            'status': 'success',
            'data': {
                'message': 'Device was successfully assigned in SADIS.'
            }
        }

        if user.status_id != 'N':
            iiq.assign_asset_to_user_by_force(device.iiq_id, user.iiq_id)

            return_response['data'].update({
                'message': 'Device was successfully assigned in SADIS and IIQ.'
            })

        return JsonResponse(return_response)

def set_owner_by_force(device, user, author):
    set_owner(device, user, author)

def remove_owner(device, author, staging = None):
    if not device.iiq_id:
        set_iiq_id(device.id)

    unassign_asset = iiq.unassign_asset(device.id)

    if device.owner != None:
        device.owner = None
        device.owner_assign_date = None
        device.owner_assign_author = None

        device.save()

    if unassign_asset.status_code == 200:
        try:
            record = StudentDeviceOwnership.objects.get(device_id = device.id)
            record.delete()

            if staging != None:
                try:
                    staged_data = DataStaging.objects.get(student_id = record.student.id)
                except:
                    staged_data = None

                if staged_data != None:
                    staged_data.device_bpi = staging['device_bpi']
                    staged_data.device_bin = staging['device_bin']

                    staged_data.save()

            return True
        except:
            return False
    else:
        return HttpResponse(content = f'Error communicating with IncidentIQ. Please submit a request for investigation with the following error code: {unassign_asset.status_code}.', status = unassign_asset.status_code)
