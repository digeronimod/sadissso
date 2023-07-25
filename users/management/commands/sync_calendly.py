# Python
import json, uuid
# Django
from django.core.management.base import BaseCommand
# SADIS
from inventory.models import CalendlyAppointment, CalendlyEvent
from inventory.utilities import is_blank
from sadis.api import api_calendly as calendly
from users.models import StudentModel, StudentAppointments

class Command(BaseCommand):
    help = 'Add all calendly appointments from JSON flatfile.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Deleting malformed appointments...'))
        CalendlyAppointment.objects.all().delete()

        for event in CalendlyEvent.objects.all():
            event_id = str(event.event_id)

            self.stdout.write(self.style.NOTICE(f'Adding appointments for event {event_id}...'))

            try:
                event_invitees = calendly.get_scheduled_event_invitees(event_uuid = event_id)

                for invitee in event_invitees:
                    CalendlyAppointment.objects.create(
                        id = uuid.uuid4(),
                        data = {
                            'payload': invitee,
                            'event': 'invitee.created'
                        }
                    )
            except:
                pass

        self.stdout.write(self.style.NOTICE('Converting appointment payloads to student data...'))
        calendly_data = CalendlyAppointment.objects.all()

        events = []
        appointments = []
        purges = []

        self.stdout.write(self.style.NOTICE('Cycling through all appointments...'))

        for appointment in calendly_data:
            appointment_id = appointment.id
            event_id = appointment.data['payload']['event'].split('/')[-1]
            good_record = 0

            if appointment.data['event'] == 'invitee.created':
                for question in appointment.data['payload']['questions_and_answers']:
                    if 'Student ID' in question['question']:
                        good_record += 1

                if good_record > 0:
                    if event_id not in events:
                        events.append(event_id)

                    if appointment_id not in appointments:
                        appointments.append(appointment_id)
                else:
                    if appointment_id not in purges:
                        purges.append(appointment_id)
            elif appointment.data['event'] == 'invitee.canceled':
                good_record = 0

                if appointment.data['payload']['rescheduled'] == False:
                    for question in appointment.data['payload']['questions_and_answers']:
                        if 'Student ID' in question['question']:
                            good_record += 1

                    if good_record > 0:
                        if event_id in events:
                            events.remove(event_id)

                        if appointment_id in appointments:
                            appointments.remove(appointment_id)

        self.stdout.write(self.style.NOTICE(f'Purging invalid records...'))

        for record_id in purges:
            record = calendly_data.get(id = record_id)
            record.delete()

        self.stdout.write(self.style.NOTICE(f'Asking for valid record event information...'))

        for event_id in events:
            if not CalendlyEvent.objects.filter(event_id = event_id).exists():
                event_data = json.loads(calendly.get_scheduled_event(event_id))

                CalendlyEvent.objects.create(
                    event_id = event_id,
                    event_name = event_data['resource']['name'],
                    event_start = event_data['resource']['start_time'],
                    event_end = event_data['resource']['end_time']
                )

                self.stdout.write(self.style.SUCCESS(f'Added event {event_id}.'))

        self.stdout.write(self.style.NOTICE('Creating appointments for valid records...'))

        for record_id in appointments:
            appointment = calendly_data.get(id = record_id)
            student_id = None
            event_id = None

            for question in appointment.data['payload']['questions_and_answers']:
                if 'Student ID' in question['question']:
                    student_id = question['answer']
                    event_id = appointment.data['payload']['event'].split('/')[-1]

            if StudentModel.objects.filter(id = student_id).exists() and StudentModel.objects.filter(id = student_id).count() == 1:
                student = StudentModel.objects.get(id = student_id)

                if CalendlyEvent.objects.filter(event_id = event_id).exists():
                    event = CalendlyEvent.objects.get(event_id = event_id)

                    if is_blank(appointment.data['payload']['text_reminder_number']):
                        scheduler_phone = 'N/A'
                    else:
                        scheduler_phone = appointment.data['payload']['text_reminder_number']

                    if not StudentAppointments.objects.filter(student_id = student.id).exists():
                        StudentAppointments.objects.create(
                            created = appointment.data['payload']['created_at'],
                            student = student,
                            event = event,
                            scheduler_name = appointment.data['payload']['name'],
                            scheduler_email = appointment.data['payload']['email'],
                            scheduler_phone = scheduler_phone
                        )

                        self.stdout.write(self.style.SUCCESS(f'Created appointment for {student.id}.'))
                    else:
                        self.stdout.write(self.style.NOTICE(f'Appointment exists for for {student.id}.'))

                    appointment.delete()
