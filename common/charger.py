# Django
from django.utils import timezone
# Application
from users.models import StudentChargerOwnership

def set_owner(charger, user, author):
    if StudentChargerOwnership.objects.filter(charger_id = charger.id).exists():
        record = StudentChargerOwnership.objects.get(charger_id = charger.id)

        if record.student:
            return False
        else:
            record.author = author
            record.date = timezone.now()
            record.student = user

            record.save()

        return True
    else:
        record = StudentChargerOwnership(
            author = author,
            charger = charger,
            student = user
        )

        record.save()

        return True

def remove_owner(charger, author):
    try:
        record = StudentChargerOwnership.objects.get(charger_id = charger.id)

        record.author = author
        record.date = timezone.now()
        record.student = None

        record.save()

        return True
    except:
        return False
