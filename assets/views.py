# Django
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
# SADIS
from inventory.models import Device
from inventory.utilities import get_query, Qurl
from users.decorators import allowed_users
from users.models import StudentModel, StudentDeviceOwnership, DataStaging

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def home(request):
    devices = Device.objects.all()
    page = request.GET.get('page', 1)

    if ('search' in request.GET) and request.GET['search'].strip():
        query_string = request.GET['search']
        search_query = get_query(query_string, ['id', 'serial'])
        entries = devices.filter(search_query).order_by('id')
    else:
        entries = devices.order_by('id')

    paginator = Paginator(entries, 50)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    context = {
        # Search
        'entries': entries
    }

    if request.method == 'POST':
        if request.POST.get('search'):
            response = redirect(Qurl(request.get_full_path()).add('search', value = request.POST.get('search')).get())
            return response

    return render(request, 'assets/index.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Administrator', 'Staff'])
def detail(request, id):
    device = get_object_or_404(Device, id = id)
    legacy_history = device.history.filter(id = device.id)

    try:
        device_ownership = StudentDeviceOwnership.objects.get(device_id = device.id)
    except:
        device_ownership = False

    if device_ownership:
        current_history = StudentDeviceOwnership.history.filter(device_id = device.id)
    else:
        current_history = False

    try:
        staged = StudentModel.objects.get(id = DataStaging.objects.filter(device_bpi = device.id).order_by("updated").last().student_id)
    except:
        staged = False

    context = {
    # QuerySets
        'device': device,
        'ownership': device_ownership,
        'legacy_history': legacy_history,
        'current_history': current_history,
        'staged': staged
    }

    if request.method == 'POST':
        if request.POST.get('action') == 'get-uuid':
            device.set_iiq_id()

    return render(request, 'assets/detail.html', context)
