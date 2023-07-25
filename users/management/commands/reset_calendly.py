# Django
from django.core.management.base import BaseCommand
# SADIS
from inventory.models import CalendlyAppointment, CalendlyEvent
from users.models import StudentAppointments

class Command(BaseCommand):
    help = 'Delete all currently Calendly information.'

    def handle(self, *args, **options):
        StudentAppointments.objects.all().delete()
        CalendlyEvent.objects.all().delete()
        CalendlyAppointment.objects.all().delete()
