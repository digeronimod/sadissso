# Python
import base64, datetime, json, requests, time
# SADIS
from users.models import DataDistribution, StudentModel

user_authorization_raw_string = 'flaglercountyRESTAPI:Fl@g13r!'
user_authorization_raw_bytes = user_authorization_raw_string.encode('utf-8')
user_authorization_base64_bytes = base64.b64encode(user_authorization_raw_bytes)
user_authorization_base64_string = user_authorization_base64_bytes.decode('utf-8')

app_authorization_raw_string = 'Flagler_county:HAIE-HJII-JHFN-EHMP-IHCP-CONL-HEDI-ALJN'
app_authorization_raw_bytes = app_authorization_raw_string.encode('utf-8')
app_authorization_base64_bytes = base64.b64encode(app_authorization_raw_bytes)
app_authorization_base64_string = app_authorization_base64_bytes.decode('utf-8')

api_url_base = 'https://www.myschoolbucks.com'
api_url_version = 'v1'

api_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Authorization': f'Basic {user_authorization_base64_string}',
    'AppAuthorization': f'Basic {app_authorization_base64_string}',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json'
}

id_client = 'MMW_110138'
provider_classlink = 'Classlink_Flagler'
provider_invoices = 'invoices_prov'

response_data = {}

## -- Utilities

def get_whois():
    api_url = f'{api_url_base}/api/{api_url_version}/user'
    api_response = requests.get(api_url, headers = api_headers)

    print(api_response.text)

def get_all_invoices():
    api_url = f'{api_url_base}/api/{api_url_version}/{id_client}/providers/{provider_invoices}/invoices'
    api_response = requests.get(api_url, headers = api_headers)

    print(api_response.text)

def get_invoices_by_student_id(student_id):
    api_url = f'{api_url_base}/api/{api_url_version}/{id_client}/providers/{provider_invoices}/invoices?searchPhrase={student_id}'
    api_response = json.loads(requests.get(api_url, headers = api_headers).text)

    if api_response and len(api_response['items']) > 0:
        return api_response['items']

def get_invoice_by_invoice_id(invoice_id):
    api_url = f'{api_url_base}/api/{api_url_version}/{id_client}/providers/{provider_invoices}/invoices/by-id/{invoice_id}'
    api_response = json.loads(requests.get(api_url, headers = api_headers).text)

    return api_response['items']

## -- Functions

def post_student_invoice(user_id, fine):
    user = StudentModel.objects.get(id = user_id)

    location_glaccount_dictionary = {
        '0000': 'glacct24',
        '0011': '0100_R_0000_3495_0011_17905',
        '0022': '0100_R_0000_3495_0022_17905',
        '0051': '0100_R_0000_3495_0051_17905',
        '0090': '0100_R_0000_3495_0090_17905',
        '0091': '0100_R_0000_3495_0091_17905',
        '0131': '0100_R_0000_3495_0131_17905',
        '0201': '0100_R_0000_3495_0201_17905',
        '0301': '0100_R_0000_3495_0301_17905',
        '0401': '0100_R_0000_3495_0401_17905',
        '7004': '0100_R_0000_3495_7004_17905'
    }

    def get_timestamp_as_hex():
        timestamp = hex(int(time.time()))

        return str(timestamp[2:].upper())

    def get_current_timestamp(fee_id = False):
        if not fee_id:
            return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            return datetime.datetime.now().strftime("MSB_%Y%m%d%H%M%S")

    def get_student_glaccount_by_location():
        for key, value in location_glaccount_dictionary.items():
            if key == user.location.id:
                return str(value)
            else:
                return 'glacct24'

    def get_student_parent_email():
        if DataDistribution.objects.filter(student_id = user.id).exists():
            distribution_data = DataDistribution.objects.get(student_id = user.id)

            return f"{user.username}@flaglercps.org, {distribution_data.parent_email}"
        else:
            return f"{user.username}@flaglercps.org"

    payload = {
        "items": [{
            "invoiceID": get_timestamp_as_hex(),
            "clientID": f"{id_client}",
            "providerID": f"{provider_invoices}",
            "storeID": 'store15',
            "departmentID": "department1",
            "invoiceDate": get_current_timestamp(fee_id = False),
            "invoiceStatus": "PENDING",
            "invoiceStatusMessage": "",
            "startDate": None,
            "endDate": None,
            "additionalEmail": get_student_parent_email(),
            "overrideEmail": "",
            "emailNotificationSent": False,
            "allowPartialPayments": True,
            "paymentScheduleID": None,
            "lateFeeEnabled": False,
            "lateFeeAmount": 0,
            "lateFeeGracePeriod": 0,
            "lateFeeInSeparateInvoice": False,
            "lateFeeGLAcctID": None,
            "lateFeeGLCashAcctID": None,
            "lateFeeGLSalesTaxAcctID": None,
            "lateFeeGLSegment": "",
            "lateFeeID": "",
            "lateFeeName": "",
            "reminders": [],
            "invoiceItems": [{
                "studentNumber": f"{user.id}",
                "invoiceItemPrice": int(fine['fine_amount']),
                "feeID": get_current_timestamp(fee_id = True),
                "feeName": f"{fine['fine_subtype']}",
                "feeType": "STANDARD",
                "paymentMethodID": "Flagler_Co_SD_Technology_Store",
                "glSegment": "",
                "reference": "",
                "teacher": "",
                "allowPartialPayments": True,
                "desc": f"{fine['fine_description']}",
                "glcashAcctID": None,
                "glsalesTaxAcctID": None,
                "glacctID": get_student_glaccount_by_location()
            }],
            "schedules": [],
            "installmentSingleStartDate": None,
            "installmentRangeStartDate": None,
            "installmentRangeEndDate": None
        }]
    }

    api_url = f'{api_url_base}/api/{api_url_version}/{id_client}/providers/{provider_invoices}/invoices'
    api_response = requests.post(api_url, headers = api_headers, data = json.dumps(payload))
    return api_response.text

def post_student_invoice_multiple(user_id, fines):
    user = StudentModel.objects.get(id = user_id)

    location_glaccount_dictionary = {
        '0000': 'glacct24',
        '0011': '0100_R_0000_3495_0011_17905',
        '0022': '0100_R_0000_3495_0022_17905',
        '0051': '0100_R_0000_3495_0051_17905',
        '0090': '0100_R_0000_3495_0090_17905',
        '0091': '0100_R_0000_3495_0091_17905',
        '0131': '0100_R_0000_3495_0131_17905',
        '0201': '0100_R_0000_3495_0201_17905',
        '0301': '0100_R_0000_3495_0301_17905',
        '0401': '0100_R_0000_3495_0401_17905',
        '7004': '0100_R_0000_3495_7004_17905'
    }

    def get_timestamp_as_hex():
        timestamp = hex(int(time.time()))

        return str(timestamp[2:].upper())

    def get_current_timestamp(fee_id = False):
        if not fee_id:
            return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            return datetime.datetime.now().strftime("MSB_%Y%m%d%H%M%S")

    def get_student_glaccount_by_location():
        for key, value in location_glaccount_dictionary.items():
            if key == user.location.id:
                return str(value)
            else:
                return 'glacct24'

    def get_student_parent_email():
        if DataDistribution.objects.filter(student_id = user.id).exists():
            distribution_data = DataDistribution.objects.get(student_id = user.id)

            return f"{user.username}@flaglercps.org, {distribution_data.parent_email}"
        else:
            return f"{user.username}@flaglercps.org"

    payload = {
        "items": [{
            "invoiceID": get_timestamp_as_hex(),
            "clientID": f"{id_client}",
            "providerID": f"{provider_invoices}",
            "storeID": 'store15',
            "departmentID": "department1",
            "invoiceDate": get_current_timestamp(fee_id = False),
            "invoiceStatus": "PENDING",
            "invoiceStatusMessage": "",
            "startDate": None,
            "endDate": None,
            "additionalEmail": get_student_parent_email(),
            "overrideEmail": "",
            "emailNotificationSent": False,
            "allowPartialPayments": True,
            "paymentScheduleID": None,
            "lateFeeEnabled": False,
            "lateFeeAmount": 0,
            "lateFeeGracePeriod": 0,
            "lateFeeInSeparateInvoice": False,
            "lateFeeGLAcctID": None,
            "lateFeeGLCashAcctID": None,
            "lateFeeGLSalesTaxAcctID": None,
            "lateFeeGLSegment": "",
            "lateFeeID": "",
            "lateFeeName": "",
            "reminders": [],
            "invoiceItems": [],
            "schedules": [],
            "installmentSingleStartDate": None,
            "installmentRangeStartDate": None,
            "installmentRangeEndDate": None
        }]
    }

    for item, data in fines.items():
        fine_item = {
            "studentNumber": f"{user.id}",
            "invoiceItemPrice": int(data['fine_amount']),
            "feeID": get_current_timestamp(fee_id = True),
            "feeName": f"{data['fine_subtype']}",
            "feeType": "STANDARD",
            "paymentMethodID": "Flagler_Co_SD_Technology_Store",
            "glSegment": "",
            "reference": "",
            "teacher": "",
            "allowPartialPayments": True,
            "desc": f"{data['fine_description']}",
            "glcashAcctID": None,
            "glsalesTaxAcctID": None,
            "glacctID": get_student_glaccount_by_location()
        }

        payload['items'][0]['invoiceItems'].append(fine_item)

    api_url = f'{api_url_base}/api/{api_url_version}/{id_client}/providers/{provider_invoices}/invoices'
    api_response = requests.post(api_url, headers = api_headers, data = json.dumps(payload))
    return api_response.text
