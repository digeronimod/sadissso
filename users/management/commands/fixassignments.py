# Django
from django.core.management.base import BaseCommand
# SADIS
from inventory.models import Device
from sadis.api import api_iiq as iiq
from users.models import StudentModel, StudentDeviceOwnership

class Command(BaseCommand):
    help = 'Assign all devices from SADIS to IIQ in list.'

    def handle(self, *args, **options):
        students = StudentModel.objects.filter(id__in = ['1822002010', '1814001004', '1820783652', '1810000681', '18230001544', '1814002228', '1821001472', '1821002607', '1818002030', '1823000001', '1897002528', '1822002521', '1822002380', '1819001236', '1897006082', '1812000707'])

        for student in students:
            ## -- 1. Make sure every student has an IIQ ID
            if student.iiq_id == None or student.iiq_id == '' or student.iiq_id == ' ' or student.iiq_id == '<Response [200]>' or student.iiq_id == '502':
                try:
                    student_iiq_data = iiq.get_user_uuid(student.id)

                    student.updated = student_iiq_data['updated']
                    student.iiq_id = student_iiq_data['iiq_id']

                    print('Updating', student.name + '...')
                    student.save()
                except:
                    print('Unable to update', student.name + '...')

            ## -- 2. Assign devices to user in IIQ (by force) since they're assigned in SADIS
            for assignment in StudentDeviceOwnership.objects.filter(student = student):
                ## -- 3. Make sure every device has an IIQ ID
                if assignment.device.iiq_id == None or assignment.device.iiq_id == '' or assignment.device.iiq_id == ' ' or assignment.device.iiq_id == '<Response [200]>' or assignment.device.iiq_id == '502':
                    try:
                        asset_uuid = iiq.get_asset_uuid(assignment.device.id)

                        print('Updating', assignment.device.id + '...')
                        assignment.device.iiq_id = asset_uuid
                        assignment.device.save()

                        ## -- 4. Try assigning the device
                        try:
                            iiq.assign_asset_to_user_by_force(assignment.device.iiq_id, student.iiq_id)
                            print('Assigned', str(assignment.device.id), 'to', str(student.id) + '...')
                        except:
                            print('Unable to assign', str(assignment.device.id), 'to', str(student.id) + '...')
                    except:
                        print('Unable to update', assignment.device.id + '...')
                else:
                    ## -- 4. Try assigning the device
                    try:
                        iiq.assign_asset_to_user_by_force(assignment.device.iiq_id, student.iiq_id)
                        print('Assigned', str(assignment.device.id), 'to', str(student.id) + '...')
                    except:
                        print('Unable to assign', str(assignment.device.id), 'to', str(student.id) + '...')

        print('Done!')
