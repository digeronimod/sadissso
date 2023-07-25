# Python
import json, requests
# Django
from django.core.management.base import BaseCommand
from django.utils import timezone
# Plugins
from constance import config as constance_config
# SADIS
from inventory.utilities import is_not_blank
from sadis.api import api_iiq as iiq
from users.models import StudentModel

api_url_base = 'https://flaglerschools.incidentiq.com/api/v1.0'
api_headers = {
    'Client': 'ApiClient',
    'Accept': 'application/json, text/plain, */*',
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {iiq.api_token}'
}

location_map = {
    '253cedcd-cd59-e811-80c3-000d3a012d41': '0011',
    '78d2335b-cd59-e811-80c3-000d3a012d41': '0022',
    'eeb94098-cd59-e811-80c3-000d3a012d41': '0051',
    'f827d955-ce59-e811-80c3-000d3a012d41': '0090',
    'd25ffc02-ce59-e811-80c3-000d3a012d41': '0091',
    '454f98b1-cd59-e811-80c3-000d3a012d41': '0131',
    '4b8f9079-cd59-e811-80c3-000d3a012d41': '0201',
    '0e1c013e-cd59-e811-80c3-000d3a012d41': '0301',
    '42d2e7e6-cd59-e811-80c3-000d3a012d41': '0401',
    '78a876ba-ce59-e811-80c3-000d3a012d41': '7004'
}

excluded_role_map = {
    '6d5fee76-e05e-43c0-b8e9-b8447746e500': 'No Access',
    '6d5fee76-e05e-43c0-b8e9-b8447746e504': 'Agent',
    '6d5fee76-e05e-43c0-b8e9-b8447746e505': 'iiQ Administrator',
    '6d5fee76-e05e-43c0-b8e9-b8447746e502': 'Faculty'
}

class Command(BaseCommand):
    help = 'Sync all students data from IncidentIQ'

    def handle(self, *args, **options):
        total_pages = iiq.get_users_page_count()
        current_page = 0

        while current_page < (total_pages + 1):
            api_url = f'{api_url_base}/users/?$s=200&$p={current_page}'
            api_response = requests.get(api_url, headers = api_headers)

            api_data = json.loads(api_response.text)
            api_data_length = len(api_data['Items'])

            if api_data_length > 0:
                print(f'Parsing page {current_page}...')

                for item in api_data['Items']:
                    data = dict(item)

                    local, at, domain = data['Username'].rpartition('@')
                    id_exists = StudentModel.objects.filter(id = data['SchoolIdNumber']).exists()
                    username_exists = StudentModel.objects.filter(username = local).exists()

                    if is_not_blank(data['SchoolIdNumber']):
                        if id_exists:
                            student = StudentModel.objects.get(id = data['SchoolIdNumber'])

                            if student.iiq_id == None or student.iiq_id == '' or student.iiq_id == ' ':
                                print('Updating', student.name + '...')

                                student.iiq_id = data['UserId']
                                student.save()
                        # else:
                        #     if data['IsActive'] == True and data['RoleId'] == '6d5fee76-e05e-43c0-b8e9-b8447746e501' and data['Location']['LocationId'] in location_map.keys():
                        #         new_student = StudentModel(
                        #             id = data['SchoolIdNumber'],
                        #             name = data['Name'],
                        #             username = local,
                        #             location_id = location_map[data['Location']['LocationId']],
                        #             status_id = 'A',
                        #             grade = data['Grade'] if data['Grade'] != '' else '00',
                        #             remote = False,
                        #             iiq_id = data['UserId'],
                        #             role = None
                        #         )
                        #
                        #         try:
                        #             new_student.save()
                        #             print(new_student.name, 'added!')
                        #         except:
                        #             pass

            current_page += 1

        constance_config.sync_iiq = timezone.now()
        print('Successfully synced all students in IncidentIQ!')
