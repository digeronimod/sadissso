# Python
import datetime, json, re, requests, string, sys
# Django
from django.http import JsonResponse
from django.utils import timezone
# Plugins
from constance import config as constance_config
# SADIS
from inventory.utilities import is_blank, is_not_blank

# Token Expires: 6/21/2026
api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1YmJiZmMwMy00YjBjLTQ4MDItYjJlYS0wMzEwMDNlZDFmOWQiLCJzY29wZSI6Imh0dHBzOi8vZmxhZ2xlcnNjaG9vbHMuaW5jaWRlbnRpcS5jb20iLCJzdWIiOiJiYTQ0MDNiNS0zOGFmLWVhMTEtOWIwNS0wMDAzZmZlNDI5YTIiLCJqdGkiOiIyY2FmODE0OS1jZjExLWVlMTEtOTA3ZS02MDQ1YmQ3ZjBhZjEiLCJpYXQiOjE2ODc1MjkyNTQuNTYzLCJleHAiOjE3ODIyMjM2NTQuNTczfQ.YtUTxVt9qHeFtolg7YcuNYaO9L3LdwfR7NJf0E4Ginw'
api_url_base = 'https://flaglerschools.incidentiq.com/api/v1.0'
api_headers = {
    'Client': 'ApiClient',
    'Accept': 'application/json, text/plain, */*',
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json; charset=utf-8',
    'Authorization': f'Bearer {api_token}'
}
api_set_only_mapped = {
    'ApiFlags': 'OnlySetMappedProperties',
}

## -- Utility
def convert_time_to_datetime(string):
    return string.replace('T', ' ')[0:-4]

def convert_location_name_to_id(name):
    from inventory.models import Location

    locations = Location.objects.all()

    for location in locations:
        if name == location.name:
            return location.id

def get_users_page_count():
    api_url = f'{api_url_base}/users/?$s=200'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        api_data = json.loads(api_response.text)
        total_pages = api_data['Paging']['PageCount']

        return total_pages

def get_assets_page_count():
    api_url = f'{api_url_base}/assets/?$s=200'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        api_data = json.loads(api_response.text)
        total_pages = api_data['Paging']['PageCount']

        return total_pages

## -- Users
def get_user_uuid(school_id):
    api_url = f'{api_url_base}/users/search/{school_id}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        data_length = len(json_response['Items'])

        if data_length > 0:
            json_data = {}
            student_data = {}

            for key, value in json_response.items():
                if key == 'Items':
                    json_data.update(value[0])

            student_data['updated'] = timezone.now()

            for key, value in json_data.items():
                if key == 'UserId':
                    student_data['iiq_id'] = value

            return student_data
        else:
            pass
    else:
        return api_response.status_code

def get_user_by_uuid(iiq_uuid):
    api_url = f'{api_url_base}/users/{iiq_uuid}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        json_data = {}
        student_data = {}

        for key, value in json_response.items():
            if key == 'Item':
                json_data.update(value)

        student_data['updated'] = timezone.now()

        for key, value in json_data.items():
            if key == 'LocationName':
                student_data['location'] = convert_location_name_to_id(value)
            if key == 'Name':
                student_data['name'] = value
            if key == 'Username':
                local, at, domain = value.rpartition('@')
                student_data['username'] = local
            if key == 'Grade':
                student_data['grade'] = value
            if key == 'RoleId':
                student_data['role_uuid'] = value

        if student_data['location'] == '0000' or student_data['role_uuid'] == '6d5fee76-e05e-43c0-b8e9-b8447746e500':
            student_data['status'] = False
            student_data['foreign_status'] = 'IA'
        else:
            student_data['status'] = True
            student_data['foreign_status'] = 'A'

        return student_data
    else:
        return api_response.status_code

def get_user_by_school_id(school_id):
    api_url = f'{api_url_base}/users/search/{school_id}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        json_data = {}
        student_data = {}

        for key, value in json_response.items():
            if key == 'Items':
                json_data.update(value[0])

        student_data['updated'] = timezone.now()

        for key, value in json_data.items():
            if key == 'LocationName':
                student_data['location'] = convert_location_name_to_id(value)
            if key == 'Name':
                student_data['name'] = value
            if key == 'Username':
                local, at, domain = value.rpartition('@')
                student_data['username'] = local
            if key == 'Grade':
                student_data['grade'] = value
            if key == 'RoleId':
                student_data['role_uuid'] = value

        if student_data['location'] == '0000' or student_data['role_uuid'] == '6d5fee76-e05e-43c0-b8e9-b8447746e500':
            student_data['status'] = False
            student_data['foreign_status'] = 'IA'
        else:
            student_data['status'] = True
            student_data['foreign_status'] = 'A'

        return student_data
    else:
        return api_response.status_code

def get_user_by_username(username):
    api_url = f'{api_url_base}/users/search/{username}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        json_data = {}
        student_data = {}

        if json_response['Paging']['TotalRows'] > 0:
            for key, value in json_response.items():
                if key == 'Items':
                    json_data.update(value[0])

            student_data['updated'] = timezone.now()

            for key, value in json_data.items():
                if key == 'SchoolIdNumber':
                    student_data['school_id'] = value
                if key == 'LocationName':
                    student_data['location'] = convert_location_name_to_id(value)
                if key == 'Name':
                    student_data['name'] = value
                if key == 'Username':
                    local, at, domain = value.rpartition('@')
                    student_data['username'] = local
                if key == 'Grade':
                    student_data['grade'] = value
                if key == 'RoleId':
                    student_data['role_uuid'] = value

            if student_data['location'] == '0000' or student_data['role_uuid'] == '6d5fee76-e05e-43c0-b8e9-b8447746e500':
                student_data['status'] = False
                student_data['foreign_status'] = 'IA'
            else:
                student_data['status'] = True
                student_data['foreign_status'] = 'A'

            return student_data
        else:
            return None
    else:
        return api_response.status_code

def change_user_location(user_uuid, location_uuid):
    api_url = f'{api_url_base}/users/{user_uuid}'
    api_headers.update(api_set_only_mapped)

    payload = '{"LocationId": ' + '"' + f'{location_uuid}' + '"}'
    api_response = requests.post(api_url, headers = api_headers, data = payload)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
    else:
        return api_response.text

def prepend_user_notes(user_uuid, note_string, user_username):
    api_url = f'{api_url_base}/users/{user_uuid}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        json_data = {}

        for key, value in json_response.items():
            if key == 'Item':
                json_data.update(value)

        existing_notes = json_data['InternalComments']
        today = datetime.date.today()

        if is_not_blank(existing_notes):
            api_headers.update(api_set_only_mapped)

            note_data = '{"InternalComments": ' + '"' + f'{today:%m/%d/%Y} ({user_username}): {note_string}\n{existing_notes}' + '"}'
            post_response = requests.post(api_url, headers = api_headers, data = note_data)
        else:
            api_headers.update(api_set_only_mapped)

            note_data = '{"InternalComments": ' + '"' + f'{today:%m/%d/%Y} ({user_username}): {note_string}' + '"}'
            post_response = requests.post(api_url, headers = api_headers, data = note_data)
    else:
        return api_response.status_code

## -- Assets

def get_asset_uuid(asset_tag):
    # get_asset_uuid('TEST1234')
    api_url = f'{api_url_base}/assets/assettag/{asset_tag}'
    response = requests.get(api_url, headers = api_headers)

    if response.status_code == 200:
        json_response = json.loads(response.text)
        data_length = len(json_response['Items'])

        if data_length > 0:
            data_details = dict(json_response['Items'][0])

            return data_details['AssetId']
        else:
            return response
    else:
        return response.status_code

def get_user_assets(user_uuid):
    api_url = f'{api_url_base}/assets/for/{user_uuid}'
    api_response = requests.get(api_url, headers = api_headers)

    assigned_assets = []

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        print(json_response)
        data_length = len(json_response['Items'])

        if data_length > 0:
            count = 0

            while count < data_length:
                for key, value in json_response['Items'][count].items():
                    if key == 'AssetTag':
                        assigned_assets.append(value)

                count += 1

            return assigned_assets
        else:
            return False
    else:
        return api_response.status_code

def get_asset_status(asset_tag):
    api_url = f'{api_url_base}/assets/assettag/{asset_tag}'
    response = requests.get(api_url, headers = api_headers)

    if response.status_code == 200:
        json_response = json.loads(response.text)
        data_length = len(json_response['Items'])
        status = {}

        if data_length > 0:
            data_details = dict(json_response['Items'][0])

            if 'Owner' in data_details.keys():
                if data_details['Owner'] == None:
                    status = {
                        'asset_id': data_details['AssetTag'],
                        'asset_uuid': data_details['AssetId'],
                        'status': 200
                    }
                else:
                    status = {
                        'asset_id': data_details['AssetTag'],
                        'asset_uuid': data_details['AssetId'],
                        'iiq_link': f'https://flaglerschools.incidentiq.com/agent/users/{data_details["Owner"]["UserId"]}',
                        'owner_school_id': data_details['Owner']['SchoolIdNumber'],
                        'owner_name': data_details['Owner']['FullName'],
                        'status': 409
                    }
            else:
                status = {
                    'asset_id': data_details['AssetTag'],
                    'asset_uuid': data_details['AssetId'],
                    'status': 200
                }

            return status
        else:
            return False
    else:
        return response.status_code

def assign_asset_to_user(asset_uuid, user_uuid):
    # assign_asset_to_user('b88b9770-35a7-ea11-9b05-0003ffe429a2', 'c2f27913-2beb-4ff8-a343-567ce203ec9b')
    api_url = f'{api_url_base}/assets/{asset_uuid}/owner'
    payload = '{\"OwnerId\":\"' + str(user_uuid) + '\",\"UpdateLastInventoryDate\":"false\",\"Force\": \"false\",\"UpdateAssetWithUserLocation\":\"true\"}'
    response = requests.post(api_url, headers = api_headers, data = payload)

    return response

def assign_asset_to_user_by_force(asset_uuid, user_uuid):
    # assign_asset_to_user_by_force('b88b9770-35a7-ea11-9b05-0003ffe429a2', 'c2f27913-2beb-4ff8-a343-567ce203ec9b')
    api_url = f'{api_url_base}/assets/{asset_uuid}/owner'
    payload = '{\"OwnerId\":\"' + str(user_uuid) + '\",\"UpdateLastInventoryDate\":"false\",\"Force\": \"true\",\"UpdateAssetWithUserLocation\":\"true\"}'
    response = requests.post(api_url, headers = api_headers, data = payload)

    return response

def unassign_asset_from_user(asset_uuid, user_uuid):
    # unassign_asset_from_user('b88b9770-35a7-ea11-9b05-0003ffe429a2', 'c2f27913-2beb-4ff8-a343-567ce203ec9b')
    api_url = f'{api_url_base}/assets/{asset_uuid}/for/{user_uuid}'
    response = requests.delete(api_url, headers = api_headers)

    if response.status_code == 200:
        return response
    else:
        return response.status_code

def unassign_asset(asset_id):
    # unassign_asset('100396')
    asset_uuid = get_asset_uuid(asset_id)

    api_url = f'{api_url_base}/assets/{asset_uuid}/remove-owner'
    response = requests.post(api_url, headers = api_headers)

    if response.status_code == 200:
        return response
    else:
        return response.status_code

def change_asset_location(asset_uuid, asset_tag, asset_serial, location_uuid):
    api_url = f'{api_url_base}/assets/{asset_uuid}'

    api_headers.update(api_set_only_mapped)

    payload = '{"AssetTag":"' + f'{asset_tag}' + '","SerialNumber":"' + f'{asset_serial}' + '","LocationId": ' + '"' + f'{location_uuid}' + '"}'
    api_response = requests.post(api_url, headers = api_headers, data = payload)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
    else:
        return api_response.text

## -- Tickets

def get_ticket_number(ticket_uuid):
    # get_ticket_number('d388ef48-b3d6-ea11-8b03-0003ffe4d4cc')
    api_url = f'{api_url_base}/tickets/{ticket_uuid}'
    response = requests.get(api_url, headers = api_headers)

    if response.status_code == 200:
        json_response = json.loads(response.text)
        data_length = len(json_response['Item'])

        if data_length > 0:
            data_details = dict(json_response['Item'])

            if 'TicketNumber' in data_details.keys():
                return data_details['TicketNumber']
        else:
            return None
    else:
        return None

def assign_ticket_agent_and_team(ticket_uuid, agent_uuid, team_uuid):
    api_url = f'{api_url_base}/tickets/{ticket_uuid}/assign'
    payload = '{"TicketId":"' + str(ticket_uuid) + '","AssignToUserId":"' + str(agent_uuid) + '","AssignToTeamId":"' + str(team_uuid) + '"}'
    api_response = requests.post(api_url, headers = api_headers, data = payload)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)

        return json_response
    else:
        return api_response.status_code

def change_ticket_description_and_location(ticket_uuid, location_uuid, ticket_description):
    api_url = f'{api_url_base}/tickets/{ticket_uuid}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        json_data = {}

        for key, value in json_response.items():
            if key == 'Item':
                json_data.update(value)

        api_headers.update(api_set_only_mapped)

        description_data = '{"IssueDescription": ' + '"' + ticket_description + '","LocationId":"' + str(location_uuid) + '"}'
        post_request = requests.post(api_url, headers = api_headers, data = description_data)

        return json.loads(post_request.text)
    else:
        return json.loads(api_response.text)

def change_ticket_owner_and_user(ticket_uuid, agent_uuid, student_uuid):
    api_url = f'{api_url_base}/tickets/{ticket_uuid}/owner/{agent_uuid}/for/{student_uuid}'
    api_response = requests.post(api_url, headers = api_headers)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)

        return json_response
    else:
        return json.loads(api_response.text)

def assign_ticket_device(ticket_id, ticket_asset_id, asset_uuid):
    # assign_ticket_device('4a67016f-82d8-0f9c-d849-42b845936c61', '4a67016f-82d8-0f9c-d849-42b845936c61', '4a67016f-82d8-0f9c-d849-42b845936c61')
    api_url = f'{api_url_base}/tickets/{ticket_id}/assets'
    payload = "[{\"TicketAssetId\":\"_ticket_asset_id_\",\"AssetId\":\"_asset_uuid_\",\"CreatedDate\":\"_asset_date_\"}]"

    replace_list = {"_ticket_asset_id_": ticket_asset_id, "_asset_uuid_": asset_uuid, "_asset_date_": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.0')}
    replace_list = dict((re.escape(k), v) for k, v in replace_list.items())
    replace_pattern = re.compile("|".join(replace_list.keys()))
    cleaned_payload = replace_pattern.sub(lambda m: replace_list[re.escape(m.group(0))], payload)

    response = requests.post(api_url, headers = api_headers, data = cleaned_payload)

    if response.status_code < 400:
        return json.loads(response.text)
    else:
        return json.loads(response.text)

def change_ticket_status_to_waiting(ticket_id):
    # change_ticket_status_to_waiting('4a67016f-82d8-0f9c-d849-42b845936c61')
    api_url = f'{api_url_base}/tickets/{ticket_id}/status/waiting-on-requestor'
    response = requests.post(api_url, headers = api_headers)

    if response.status_code == 200:
        return True
    else:
        return False

def close_ticket(ticket_id):
    # close_ticket('4a67016f-82d8-0f9c-d849-42b845936c61')
    api_url = f'{api_url_base}/tickets/{ticket_id}/close'
    response = requests.post(api_url, headers = api_headers)

    if response.status_code == 200:
        return True
    else:
        return False

def create_new_student_device_ticket(location_id):
    api_url = f'{api_url_base}/tickets-templates/4a67016f-82d8-0f9c-d849-42b845936c61/new-ticket'
    response = requests.post(api_url, headers = api_headers)

    if response.status_code == 200 or response.status_code == 201:
        json_response = json.loads(response.text)

        # BES
        if location_id == '0022':
            agent_uuid = constance_config.bes_lead
            team_uuid = constance_config.bes_iiq_team_id
            location_uuid = constance_config.bes_iiq_location_id
        # OKES
        elif location_id == '0201':
            agent_uuid = constance_config.okes_lead
            team_uuid = constance_config.okes_iiq_team_id
            location_uuid = constance_config.okes_iiq_location_id
        # RES
        elif location_id == '0051':
            agent_uuid = constance_config.res_lead
            team_uuid = constance_config.res_iiq_team_id
            location_uuid = constance_config.res_iiq_location_id
        # WES
        elif location_id == '0131':
            agent_uuid = constance_config.wes_lead
            team_uuid = constance_config.wes_iiq_team_id
            location_uuid = constance_config.wes_iiq_location_id
        # BTES
        elif location_id == '0301':
            agent_uuid = constance_config.btes_lead
            team_uuid = constance_config.btes_iiq_team_id
            location_uuid = constance_config.btes_iiq_location_id
        # BTMS
        elif location_id == '0011':
            agent_uuid = constance_config.btms_lead
            team_uuid = constance_config.btms_iiq_team_id
            location_uuid = constance_config.btms_iiq_location_id
        # ITMS
        elif location_id == '0401':
            agent_uuid = constance_config.itms_lead
            team_uuid = constance_config.itms_iiq_team_id
            location_uuid = constance_config.itms_iiq_location_id
        # FPC
        elif location_id == '0091':
            agent_uuid = constance_config.fpc_lead
            team_uuid = constance_config.fpc_iiq_team_id
            location_uuid = constance_config.fpc_iiq_location_id
        # MHS/iFlagler
        elif location_id == '0090' or location_id == '7004':
            agent_uuid = constance_config.mhs_lead
            team_uuid = constance_config.mhs_iiq_team_id
            location_uuid = constance_config.mhs_iiq_location_id
        # New Student Device
        else:
            agent_uuid = 'ba4403b5-38af-ea11-9b05-0003ffe429a2'# FCSBapi .
            team_uuid = '19d632a4-06c5-ea11-8b03-0003ffe4d4cc'# New Student Device
            location_uuid = '2c049ff5-22fb-404b-965b-93ed518cd8ec'# Government Services Building

        if is_not_blank(json_response['Item']['TicketId']):
            response_data = {
                'ticket_id': json_response['Item']['TicketId'],
                'agent_uuid': agent_uuid,
                'team_uuid': team_uuid,
                'location_uuid': location_uuid
            }

            return response_data
        else:
            return None
    else:
        return None

def create_device_checkin_ticket(location_id):
    api_url = f'{api_url_base}/tickets-templates/bd63ba4e-d463-a610-511e-9e3bf5370a27/new-ticket'
    response = requests.post(api_url, headers = api_headers)

    if response.status_code < 400:
        json_response = json.loads(response.text)

        # BES
        if location_id == '0022':
            agent_uuid = constance_config.bes_lead
            team_uuid = constance_config.bes_iiq_team_id
            location_uuid = constance_config.bes_iiq_location_id
        # OKES
        elif location_id == '0201':
            agent_uuid = constance_config.okes_lead
            team_uuid = constance_config.okes_iiq_team_id
            location_uuid = constance_config.okes_iiq_location_id
        # RES
        elif location_id == '0051':
            agent_uuid = constance_config.res_lead
            team_uuid = constance_config.res_iiq_team_id
            location_uuid = constance_config.res_iiq_location_id
        # WES
        elif location_id == '0131':
            agent_uuid = constance_config.wes_lead
            team_uuid = constance_config.wes_iiq_team_id
            location_uuid = constance_config.wes_iiq_location_id
        # BTES
        elif location_id == '0301':
            agent_uuid = constance_config.btes_lead
            team_uuid = constance_config.btes_iiq_team_id
            location_uuid = constance_config.btes_iiq_location_id
        # BTMS
        elif location_id == '0011':
            agent_uuid = constance_config.btms_lead
            team_uuid = constance_config.btms_iiq_team_id
            location_uuid = constance_config.btms_iiq_location_id
        # ITMS
        elif location_id == '0401':
            agent_uuid = constance_config.itms_lead
            team_uuid = constance_config.itms_iiq_team_id
            location_uuid = constance_config.itms_iiq_location_id
        # FPC
        elif location_id == '0091':
            agent_uuid = constance_config.fpc_lead
            team_uuid = constance_config.fpc_iiq_team_id
            location_uuid = constance_config.fpc_iiq_location_id
        # MHS/iFlagler
        elif location_id == '0090' or location_id == '7004':
            agent_uuid = constance_config.mhs_lead
            team_uuid = constance_config.mhs_iiq_team_id
            location_uuid = constance_config.mhs_iiq_location_id
        # New Student Device
        else:
            agent_uuid = 'ba4403b5-38af-ea11-9b05-0003ffe429a2'# FCSBapi .
            team_uuid = '19d632a4-06c5-ea11-8b03-0003ffe4d4cc'# New Student Device
            location_uuid = '2c049ff5-22fb-404b-965b-93ed518cd8ec'# Government Services Building

        if is_not_blank(json_response['Item']['TicketId']):
            response_data = {
                'ticket_id': json_response['Item']['TicketId'],
                'ticket_asset_id': json_response['Item']['Assets'][0]['TicketAssetId'],
                'agent_uuid': agent_uuid,
                'team_uuid': team_uuid,
                'location_uuid': location_uuid
            }

            return response_data
        else:
            return None
    else:
        return None

def create_new_student_transfer_ticket(location_id):
    from inventory.models import Location

    api_url = f'{api_url_base}/tickets-templates/cb81215e-3816-1327-f3dd-397925e725eb/new-ticket'
    response = requests.post(api_url, headers = api_headers)

    if response.status_code == 200 or response.status_code == 201:
        json_response = json.loads(response.text)

        # BES
        if location_id == '0022':
            agent_uuid = constance_config.bes_lead
            team_uuid = constance_config.bes_iiq_team_id
            location_uuid = constance_config.bes_iiq_location_id
            notify_recipient = [constance_config.bes_registrar, constance_config.bes_agent]
        # OKES
        elif location_id == '0201':
            agent_uuid = constance_config.okes_lead
            team_uuid = constance_config.okes_iiq_team_id
            location_uuid = constance_config.okes_iiq_location_id
            notify_recipient = [constance_config.okes_registrar, constance_config.okes_agent]
        # RES
        elif location_id == '0051':
            agent_uuid = constance_config.res_lead
            team_uuid = constance_config.res_iiq_team_id
            location_uuid = constance_config.res_iiq_location_id
            notify_recipient = [constance_config.res_registrar, constance_config.res_agent]
        # WES
        elif location_id == '0131':
            agent_uuid = constance_config.wes_lead
            team_uuid = constance_config.wes_iiq_team_id
            location_uuid = constance_config.wes_iiq_location_id
            notify_recipient = [constance_config.wes_registrar, constance_config.wes_agent]
        # BTES
        elif location_id == '0301':
            agent_uuid = constance_config.btes_lead
            team_uuid = constance_config.btes_iiq_team_id
            location_uuid = constance_config.btes_iiq_location_id
            notify_recipient = [constance_config.btes_registrar, constance_config.btes_agent]
        # BTMS
        elif location_id == '0011':
            agent_uuid = constance_config.btms_lead
            team_uuid = constance_config.btms_iiq_team_id
            location_uuid = constance_config.btms_iiq_location_id
            notify_recipient = [constance_config.btms_registrar, constance_config.btms_agent]
        # ITMS
        elif location_id == '0401':
            agent_uuid = constance_config.itms_lead
            team_uuid = constance_config.itms_iiq_team_id
            location_uuid = constance_config.itms_iiq_location_id
            notify_recipient = [constance_config.itms_registrar, constance_config.itms_agent]
        # FPC
        elif location_id == '0091':
            agent_uuid = constance_config.fpc_lead
            team_uuid = constance_config.fpc_iiq_team_id
            location_uuid = constance_config.fpc_iiq_location_id
            notify_recipient = [constance_config.fpc_registrar, constance_config.fpc_agent]
        # MHS/iFlagler
        elif location_id == '0090' or location_id == '7004':
            agent_uuid = constance_config.mhs_lead
            team_uuid = constance_config.mhs_iiq_team_id
            location_uuid = constance_config.mhs_iiq_location_id
            notify_recipient = [constance_config.mhs_registrar, constance_config.mhs_agent]
        # New Student Device
        else:
            agent_uuid = 'ba4403b5-38af-ea11-9b05-0003ffe429a2'# FCSBapi .
            team_uuid = '19d632a4-06c5-ea11-8b03-0003ffe4d4cc'# New Student Device
            location_uuid = '2c049ff5-22fb-404b-965b-93ed518cd8ec'# Government Services Building
            notify_recipient = ['winslowc@flaglerschools.com']

        if is_not_blank(json_response['Item']['TicketId']):
            response_data = {
                'ticket_id': json_response['Item']['TicketId'],
                'ticket_asset_id': json_response['Item']['Assets'][0]['TicketAssetId'],
                'agent_uuid': agent_uuid,
                'team_uuid': team_uuid,
                'location_uuid': location_uuid,
                'notify_recipient': notify_recipient
            }

            return response_data
        else:
            return None
    else:
        return None

# create_ticket = create_device_checkin_ticket(LOCATION_ID)
# assign_ticket_device = assign_ticket_device(create_ticket['ticket_id'], create_ticket['ticket_asset_id'], ASSET_IIQ_UUID)
# update_ticket = change_ticket_description_and_location(create_ticket['ticket_id'], create_ticket['location_uuid'], TICKET_DESCRIPTION)
# assign_ticket_agent = assign_ticket_agent_and_team(create_ticket['ticket_id'], create_ticket['agent_uuid'], create_ticket['team_uuid'])
# assign_ticket_student = change_ticket_owner_and_user(create_ticket['ticket_id'], create_ticket['agent_uuid'], STUDENT_IIQ_UUID)
