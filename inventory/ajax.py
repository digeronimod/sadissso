# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# SADIS
from inventory.models import Device
from users.decorators import allowed_users
from users.models import DataCollection, DataStaging

response_data = {
    'response_code': None,
    'response_message': None
}

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrator', 'Staff', 'Viewer'])
def collections_bin_change(request):
    try:
        device = Device.objects.get(id = request.POST.get('device'))
    except:
        device = False

    if device:
        device.bin = request.POST.get('bin')
        device.save()

        try:
            collection_data = DataCollection.objects.get(device_id = request.POST.get('device'))
        except:
            collection_data = False

        if collection_data:
            collection_data.device_bin = request.POST.get('bin')
            collection_data.save()

        try:
            staging_data = DataStaging.objects.filter(device_bpi = request.POST.get('device'))
        except:
            staging_data = False

        if staging_data.count() > 0:
            for entry in staging_data:
                entry.device_bin = request.POST.get('bin')
                entry.save()

    if device and collection_data:
        response_data['response_code'] = 101
    elif device and not collection_data:
        response_data['response_code'] = 201
    else:
        response_data['response_code'] = 301

    return JsonResponse(response_data)
