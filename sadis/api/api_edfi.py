# Python
import datetime, json, re, requests, string, sys
from urllib import parse
# Django
from django.utils import timezone
from django.conf import settings

## -- GENERAL CONFIGURATION
api_key = 'B5C2A4A09F75478F'
api_secret = 'F6DAE3232F074104A481C657'

## -- OAUTH CONFIGURATION
oauth_url_base = ''
oauth_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

## -- OAUTH FUNCTIONS (PART 1)
def get_access_token():
    with open(f'{settings.BASE_DIR}/sadis/api/edfi_api.token', 'r') as token_file:
        api_token = token_file.readline().strip()

    if api_token != None or api_token != '':
        return api_token
    else:
        return None

## -- API CONFIGURATION
api_headers = {
    'Client': 'ApiClient',
    'Accept': 'application/json, text/plain, */*',
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {get_access_token()}'
}

## -- OAUTH FUNCTIONS (PART 2)
def refresh_access_token():
    code_url = f'https://edfiapi.nefec.org/v2/api/oauth/authorize?client_id={api_key}&response_type=code'
    code_response = json.loads(requests.get(code_url, headers = oauth_headers).text)

    if 'code' in code_response.keys():
        refresh_token = code_response['code']
    else:
        refresh_token = None

    if refresh_token != None:
        token_url = f'https://edfiapi.nefec.org/v2/api/oauth/token'
        token_data = {"client_id": api_key, "client_secret": api_secret, "code": refresh_token, "grant_type": "authorization_code"}
        token_response = json.loads(requests.post(token_url, data = token_data, headers = oauth_headers).text)

        if 'access_token' in token_response.keys():
            with open(f'{settings.BASE_DIR}/sadis/api/edfi_api.token', 'w') as token_file:
                token_file.write(token_response['access_token'])

            api_headers['Authorization'] = f'Bearer {token_response["access_token"]}'

## -- GLOBAL VARIABLES
response_data = {}

## -- SPECIFIC FUNCTIONS
def get_students_data(offset = 0, year = '2024'):
    api_url = f'https://edfiapi.nefec.org/v2/api/api/v2.0/{year}/students?limit=100&offset={offset}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code != 200:
        refresh_access_token()

        api_response = requests.get(api_url, headers = api_headers)

    return json.loads(api_response.text)

def get_staffs_data(offset = 0, year = '2024'):
    api_url = f'https://edfiapi.nefec.org/v2/api/api/v2.0/{year}/staffs?limit=100&offset={offset}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code != 200:
        refresh_access_token()

        api_response = requests.get(api_url, headers = api_headers)

    return json.loads(api_response.text)

def get_students_additional_data(offset = 0, year = '2024'):
    api_url = f'https://edfiapi.nefec.org/v2/api/api/v2.0/{year}/studentSchoolAssociations?limit=100&offset={offset}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code != 200:
        refresh_access_token()

        api_response = requests.get(api_url, headers = api_headers)

    return json.loads(api_response.text)

def get_staffs_additional_data(offset = 0, year = '2024'):
    api_url = f'https://edfiapi.nefec.org/v2/api/api/v2.0/{year}/staffSchoolAssociations?limit=100&offset={offset}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code != 200:
        refresh_access_token()

        api_response = requests.get(api_url, headers = api_headers)

    return json.loads(api_response.text)

def get_student_by_fleid(fleid = 0, year = '2024'):
    api_url = f'https://edfiapi.nefec.org/v2/api/api/v2.0/{year}/students?studentUniqueId={fleid}'
    api_response = requests.get(api_url, headers = api_headers)

    if api_response.status_code != 200:
        refresh_access_token()

        api_response = requests.get(api_url, headers = api_headers)

    return json.loads(api_response.text)
