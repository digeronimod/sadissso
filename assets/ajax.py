# Django
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# SADIS
from inventory.models import Device
from inventory.utilities import is_not_blank
from users.decorators import allowed_users
from users.models import DataStaging

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def update_device_bin(request):
    device = Device.objects.get(id = request.POST.get('device_id'))
    new_bin = request.POST.get('new_bin')

    if is_not_blank(new_bin):
        device.bin = new_bin
        device.save()

        if DataStaging.objects.filter(device_bpi = device.id).exists():
            staging = DataStaging.objects.get(device_bpi = device.id)
            staging.device_bin = new_bin
            staging.save()

        return JsonResponse({
            'code': 200,
            'message': 'Successfully updated device bin.'
        })
    else:
        return JsonResponse({
            'code': 400,
            'message': 'Unable to update device bin.'
        })
