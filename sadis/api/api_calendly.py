# Python
import json, requests

def is_blank(string):
    return not (string and string.strip())

def is_not_blank(string):
    return bool(string and string.strip())

access_token = 'eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjg2OTMzMTc5LCJqdGkiOiI5YjQ4NDI4YS00YWI5LTRjZTAtODEwNS1mYmVjOGNhMjQ1Y2IiLCJ1c2VyX3V1aWQiOiJGQ0hDU1JBTElVRDZQVUZYIn0.lzHWh4ll4q3qOSGN63UQ-Y0AbMd1jsjhhgdPaeGQyYsS0nCoeqhOjFcN9hdmKTlBi9sy6iD8YRlu5adzqH-3qw'
organization = 'https://api.calendly.com/organizations/DECCOAJRZFYYECHL'
url_base = 'https://api.calendly.com'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

def get_me():
    url = f'{url_base}/users/me'

    response = requests.request(method = 'GET', url = url, headers = headers)

    return response.text

def get_user(uuid):
    url = f'{url_base}/users/{uuid}'

    response = requests.request(method = 'GET', url = url, headers = headers)

    return response.text

def get_event_types():
    url = f'{url_base}/event_types'

    query = {'active': True, 'count': 100, 'organization': organization}
    response = requests.request(method = 'GET', url = url, params = query, headers = headers)

    with open('calendly_event_types.json', 'w+') as outfile:
       json.dump(json.loads(response.text), outfile, indent = 4)

def get_scheduled_events(event_data = [], next_page = None, current_page = 1, start_time = None, end_time = None):
    if next_page == None:
        url = f'{url_base}/scheduled_events'
    else:
        url = next_page

    query = {'count': 100, 'organization': organization, 'status': 'active', 'min_start_time': start_time, 'max_start_time': end_time}

    if next_page == None:
        event_data = []
        response = requests.request(method = 'GET', url = url, params = query, headers = headers)
    else:
        response = requests.request(method = 'GET', url = url, headers = headers)

    with open(f'/home/sysadmin/sadis/sadis/api/calendly_appointments/scheduled_events_p{current_page}.json', 'w') as outfile:
        json.dump(json.loads(response.text), outfile, indent = 4)

    data = json.loads(response.text)

    for event in data['collection']:
        event_data.append(event)

    if data['pagination']['next_page'] != None:
        get_scheduled_events(next_page = data['pagination']['next_page'], current_page = current_page + 1, start_time = start_time, end_time = end_time)
        
    return event_data

def get_scheduled_event(event_uuid = None):
    url = f'{url_base}/scheduled_events/{event_uuid}'
    response = requests.request(method = 'GET', url = url, headers = headers)

    return response.text

user_data = []

def get_scheduled_event_invitees(user_data = [], event_uuid = None, next_page = None, current_page = 1):
    if next_page == None:
        user_data = []
        url = f'{url_base}/scheduled_events/{event_uuid}/invitees'
    else:
        url = f'{next_page}'

    query = {'count': 100, 'organization': organization, 'status': 'active'}

    if next_page == None:
        response = requests.request('GET', url, params = query, headers = headers)
    else:
        response = requests.request('GET', url, headers = headers)

    with open(f'sadis/api/calendly_appointments/{event_uuid}_invitees.json', 'w') as outfile:
        json.dump(json.loads(response.text), outfile, indent = 4)

    data = json.loads(response.text)

    for invitee in data['collection']:
        user_data.append(invitee)

    if data['pagination']['next_page'] != None:
        get_scheduled_event_invitees(next_page = data['pagination']['next_page'], current_page = current_page + 1)
    
    return user_data

#get_me()
#get_user(uuid = '673417c7-3494-4fec-b4f1-76e47d93c410')
#get_event_types()
#get_scheduled_events()
#get_scheduled_event('4bb2459e-cc9e-48c4-b80a-1299d74e066d')
#get_scheduled_event_invitees('4bb2459e-cc9e-48c4-b80a-1299d74e066d')
