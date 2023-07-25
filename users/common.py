# Django
from django.http import JsonResponse
# Application
from inventory.models import Device, Note
from users.models import DataDistributionArchive

def add_note_to_user(author, user, note):
    object = Note.objects.create(item_id = user.id, body = note, author = author)

    if object.pk:
        response = {
            'code': 200,
            'message': f"Successfully added the note to {user.name}'s account."
        }
    else:
        response = {
            'code': 600,
            'message': "Unable to create or add the note to the user's account. Please try again. If the issue persists, please contacnt your school's Technology Support Technician for additional troubleshooting steps."
        }

    return JsonResponse(response)

def archive_dlmr_record(record):
    archive_object = DataDistributionArchive()

    for field in record._meta.fields:
        setattr(archive_object, field.name, getattr(record, field.name))

    archive_object.save()
    record.delete()

def assign_charger(student_id, device_id):
    device = Device.objects.filter(id = device_id)

    if 'MacBook' in device.foreign_model.name:
        if 'M1' in device.foreign_model.name:
            # ASSIGN USB-C LAPTOP CHARGER
            ...
        else:
            # ASSIGN USB-A LAPTOP CHARGER
            ...

    if 'iPad' in device.foreign_model.name:
        if 'iPad 8' in device.foreign_model.name:
            # ASSIGN USB-C TABLET CHARGER
            ...
        else:
            # ASSIGN USB-A TABLET CHARGER
            ...
