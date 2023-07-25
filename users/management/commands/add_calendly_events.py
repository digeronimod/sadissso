# Python
import json
# Django
from django.core.management.base import BaseCommand
# SADIS
from sadis.api import api_calendly as calendly
from inventory.models import CalendlyEvent

class Command(BaseCommand):
    help = 'Add all calendly events from Calendly.'

    def handle(self, *args, **options):
        start_time = '2023-07-10T00:00:00.000000Z'
        end_time = '2023-12-25T00:00:00.000000Z'

        event_data = calendly.get_scheduled_events(start_time = start_time, end_time = end_time)

        for event in event_data:
            event_id = event['uri'].split('/')[-1]

            if not CalendlyEvent.objects.filter(event_id = event_id).exists():
                print(f'Adding event {event_id} to event database...')

                CalendlyEvent.objects.create(
                    event_id = event_id,
                    event_name = event['name'],
                    event_start = event['start_time'],
                    event_end = event['end_time']
                )

        print('Done getting Calendly events!')
