# Python
import datetime, uuid
# Django
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
# Plugins
from simple_history.models import HistoricalRecords
# SADIS
from inventory.models import CalendlyEvent, Charger, Device, FineTypes, FineSubtypes, Location, LocationCode, Person, PersonPrograms
from inventory.utilities import is_not_blank, make_ordinal

class Student(Person):
    fleid = models.CharField(max_length = 20, null = True, blank = True)
    grade = models.CharField(max_length = 3, null = True, blank = True)
    role = models.ForeignKey('StudentRole', null = True, on_delete = models.SET_NULL)
    remote = models.BooleanField(default = 0)
    password = models.CharField(max_length = 25, null = True, blank = True)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True

        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving

        return ret

    def set_role(self, role_object):
        self.role = role_object
        self.save()

    def get_grade(self, full = False):
            if self.grade == '00' or self.grade == '' or self.grade == None:
                return 'None'
            else:
                return make_ordinal(self.grade)

    def get_grade_full(self):
        if is_not_blank(self.grade):
            if self.grade == 'PK':
                return 'Pre-Kindergarten'
            elif self.grade == 'KG':
                return 'Kindergarten'
            elif self.grade == 'GD':
                return 'Graduated'
            else:
                return f'{make_ordinal(self.grade)} Grade'
        else:
            return 'None'

    def get_role_id(self):
        if self.role:
            return self.role.id
        else:
            return 'None'

    def get_role_name(self):
        if self.role:
            return self.role.name
        else:
            return 'None'

    def get_remote_status(self):
        if self.remote:
            return 'Yes'
        else:
            return 'No'

class StudentModel(models.Model):
    id = models.CharField(max_length = 15, primary_key = True, unique = True, verbose_name = 'ID')
    unique_id = models.CharField(max_length = 20, unique = True, null = True, blank = True)
    iiq_id = models.UUIDField(null = True, blank = True)
    updated = models.DateTimeField(default = datetime.datetime(1988, 6, 1, 8, 0, 0))
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    name = models.CharField(max_length = 50)
    username = models.CharField(max_length = 30, unique = True)
    location = models.ForeignKey(Location, null = True, on_delete = models.SET_NULL)
    location_code = models.ForeignKey(LocationCode, null = True, blank = True, on_delete = models.SET_NULL)
    status = models.ForeignKey('StudentStatuses', null = True, on_delete = models.SET_NULL)
    role = models.ForeignKey('StudentRole', null = True, on_delete = models.SET_NULL)
    grade = models.CharField(max_length = 3, null = True, blank = True)
    remote = models.BooleanField(default = 0)

    password = models.CharField(max_length = 25, null = True, blank = True)
    birthdate = models.DateField(null = True, blank = True)
    withdraw_date = models.DateField(null = True, blank = True)
    graduation_date = models.DateField(null = True, blank = True)

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True

        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving

        return ret

    def set_role(self, role_object):
        self.role = role_object
        self.save()

    def get_role_id(self):
        if self.role != None:
            return self.role.id
        else:
            return 'None'

    def get_role(self):
        if self.role:
            return self.role.name
        else:
            return 'None'

    def get_grade(self, full = False):
            if self.grade == '00' or self.grade == '' or self.grade == None:
                return 'None'
            else:
                return make_ordinal(self.grade)

    def get_grade_full(self):
        if is_not_blank(self.grade):
            if self.grade == 'PK':
                return 'Pre-Kindergarten'
            elif self.grade == 'KG':
                return 'Kindergarten'
            elif self.grade == 'GD':
                return 'Graduated'
            else:
                return f'{make_ordinal(self.grade)} Grade'
        else:
            return 'None'

    def get_remote_status(self):
        if self.remote == 1:
            return 'Yes'
        else:
            return 'No'

    def get_status_id(self):
        if self.status:
            return self.status.id
        else:
            return 'None'

    def get_status(self):
        if self.status:
            return self.status.name
        else:
            return 'None'

    def get_location_code(self):
        if self.location_code:
            return f'({self.location_code.id}) {self.location_code.name}'

    class Meta:
        ordering = ['id', 'name']
        verbose_name = 'Student (Ed-Fi)'
        verbose_name_plural = 'Students (Ed-Fi)'

    def __str__(self):
        return self.name

class StudentModelIDLog(models.Model):
    id = models.UUIDField(primary_key = True, unique = True, default = uuid.uuid4)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)
    date = models.DateTimeField(null = True, default = timezone.now)

    student = models.ForeignKey(StudentModel, null = True, blank = True, on_delete = models.SET_NULL)

    class Meta:
        verbose_name = 'Student: ID Log'
        verbose_name_plural = 'Student: ID Logs'

    def __str__(self):
        return self.student.name

class StudentDeviceOwnership(models.Model):
    id = models.UUIDField(primary_key = True, unique = True, default = uuid.uuid4)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)
    date = models.DateTimeField(null = True, default = timezone.now)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    student = models.ForeignKey(StudentModel, null = True, blank = True, on_delete = models.SET_NULL)
    device = models.ForeignKey(Device, null = True, blank = True, on_delete = models.SET_NULL)

    class Meta:
        verbose_name = 'Student: Device Ownership'
        verbose_name_plural = 'Student: Devices Ownership'

    def __str__(self):
        return f'{self.device.id}: {self.student.id}'

class StudentChargerOwnership(models.Model):
    id = models.UUIDField(primary_key = True, unique = True, default = uuid.uuid4)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)
    date = models.DateTimeField(null = True, default = timezone.now)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    student = models.ForeignKey(StudentModel, null = True, blank = True, on_delete = models.SET_NULL)
    charger = models.ForeignKey(Charger, null = True, blank = True, on_delete = models.SET_NULL)

    class Meta:
        verbose_name = 'Student: Charger Ownership'
        verbose_name_plural = 'Student: Charger Ownership'

    def __str__(self):
        return f'{self.charger}: {self.student}'

class StudentStatuses(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Student Status'
        verbose_name_plural = 'Student Statuses'

    def __str__(self):
        return self.name

class StudentRole(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Student Role'
        verbose_name_plural = 'Student Roles'

    def __str__(self):
        return self.name

class StudentFines(models.Model):
    STATUS_CHOICES = (
        ('P', 'Paid'),
        ('UP', 'Unpaid')
    )

    student = models.ForeignKey(Student, null = True, on_delete = models.CASCADE, related_name = 'student_fine')
    fine_type = models.ForeignKey(FineTypes, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'fine_type')
    fine_subtype = models.ForeignKey(FineSubtypes, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'fine_subtype')
    created = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)
    status = models.CharField(max_length = 2, choices = STATUS_CHOICES, default = 'UP', null = True, blank = True)
    device = models.ForeignKey(Device, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'devices')
    location = models.ForeignKey(Location, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'locations')
    updated = models.DateTimeField(auto_now = True)
    amount = models.DecimalField(max_digits = 6, decimal_places = 2, null = True, blank = True, default = '0.00')
    paid = models.DecimalField(max_digits = 6, decimal_places = 2, null = True, blank = True, default = '0.00')
    note = models.TextField(null = True, blank = True)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    class Meta:
        verbose_name = 'Student Fine'
        verbose_name_plural = 'Student Fines'

    def get_value(self):
        return self.amount

    def __str__(self):
        if self.fine_type:
            return f'{self.fine_type.name}: {self.fine_subtype.name}'
        else:
            return self.fine_subtype.name

class StudentFinesExport(models.Model):
    STATUS_CHOICES = (
        ('P', 'Paid'),
        ('UP', 'Unpaid')
    )

    student = models.ForeignKey(Student, null=True, on_delete=models.CASCADE, related_name='student_fine_export')
    fine_type = models.ForeignKey(FineTypes, null=True, blank=True, on_delete=models.SET_NULL, related_name='fine_type_export')
    fine_subtype = models.ForeignKey(FineSubtypes, null=True, blank=True, on_delete=models.SET_NULL, related_name='fine_subtype_export')
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='UP', null=True, blank=True)
    device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.SET_NULL, related_name='devices_export')
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='locations_export')
    updated = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default='0.00')
    paid = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default='0.00')
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Student Fine'
        verbose_name_plural = 'Student Fines'

    def get_value(self):
        return self.amount

    def __str__(self):
        if self.fine_type:
            return f'{self.fine_type.name}: {self.fine_subtype.name}'
        else:
            return self.fine_subtype.name

class StudentModelPrograms(models.Model):
    id = models.UUIDField(primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    student = models.OneToOneField(StudentModel, null = True, on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)

    program = models.ForeignKey(PersonPrograms, null = True, on_delete = models.SET_NULL)

    class Meta:
        ordering = ['created']
        verbose_name = 'Student Program Enrollment'
        verbose_name_plural = 'Student Program Enrollments'

    def __str__(self):
        return f'{self.student.name}: {self.program.id}'

class StudentTransfers(models.Model):
    id = models.CharField(max_length = 40, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    iiq_id = models.CharField(max_length = 40, null = True, blank = True)
    student = models.OneToOneField(StudentModel, null = True, on_delete = models.CASCADE, related_name = 'student_transfer')
    created = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)

    transfer_from = models.ForeignKey(Location, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'transfer_from')
    transfer_to = models.ForeignKey(Location, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'transfer_to')

    class Meta:
        verbose_name = 'Student Transfer'
        verbose_name_plural = 'Student Transfers'

    def __str__(self):
        return f'{self.student.name}: {self.transfer_from.name} > {self.transfer_to.name}'

class StudentAppointments(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    created = models.DateTimeField()

    student = models.ForeignKey(StudentModel, null = True, on_delete = models.CASCADE, related_name = 'student_appointment')
    event = models.ForeignKey(CalendlyEvent, null = True, blank = False, on_delete = models.SET_NULL)

    scheduler_name = models.CharField(max_length = 50)
    scheduler_email = models.CharField(max_length = 250)
    scheduler_phone = models.CharField(max_length = 25)

    class Meta:
        verbose_name = 'Student Appointment'
        verbose_name_plural = 'Student Appointments'

    def __str__(self):
        return f'{self.student.name}: {self.event_id}'

class StaffModel(models.Model):
    id = models.CharField(max_length = 15, primary_key = True, unique = True, verbose_name = 'ID')
    unique_id = models.CharField(max_length = 20, unique = True, null = True, blank = True)
    iiq_id = models.UUIDField(null = True, blank = True)
    updated = models.DateTimeField(default = datetime.datetime(1988, 6, 1, 8, 0, 0))
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    name = models.CharField(max_length = 50)
    username = models.CharField(max_length = 30, unique = True)
    location = models.ForeignKey(Location, null = True, on_delete = models.SET_NULL)

    password = models.CharField(max_length = 25, null = True, blank = True)
    birthdate = models.DateField(null = True, blank = True)

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True

        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving

        return ret

    def get_status(self):
        if self.status:
            return self.status.name
        else:
            return 'None'

    class Meta:
        ordering = ['id', 'name']
        verbose_name = 'Staff (Ed-Fi)'
        verbose_name_plural = 'Staff (Ed-Fi)'

    def __str__(self):
        return self.name

class DataStaging(models.Model):
    student_id = models.CharField(max_length = 15, primary_key = True, unique = True, verbose_name = 'ID')

    created = models.DateTimeField(auto_now_add = True, null = True)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))
    updated = models.DateTimeField(auto_now = True, null = True)

    device_bpi = models.CharField(max_length = 10, null = True)
    device_bin = models.CharField(max_length = 10, null = True)

    class Meta:
        ordering = ['student_id']
        verbose_name = 'Staging Data'
        verbose_name_plural = 'Staging Data'

    def __str__(self):
        return self.student_id

class DataCollection(models.Model):
    DEVICE_RETURN_TYPE = (
        ('DRSR', 'Device Returned (Summer Refresh)'),
        ('DRNR', 'Device Returned (Not Returning)')
    )

    CHARGER_RETURN_TYPE = (
        ('CR', 'Charger Returned'),
        ('CNR', 'Charger Not Returned'),
        ('CNRSR', 'Charger Not Returned (Summer Refresh)')
    )

    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4)
    device = models.ForeignKey(Device, null = True, on_delete = models.SET_NULL)
    student = models.ForeignKey(Student, null = True, on_delete = models.SET_NULL)

    created = models.DateTimeField(auto_now_add = True, null = True)
    updated = models.DateTimeField(auto_now = True, null = True)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)

    student_next_location = models.ForeignKey(Location, null = True, on_delete = models.SET_NULL)
    student_next_grade = models.CharField(max_length = 2, null = True)

    parent_address = models.CharField(max_length = 150, null = True)
    parent_email = models.EmailField(null = True)
    parent_name = models.CharField(max_length = 50, null = True)
    parent_phone = models.CharField(max_length = 15, null = True)

    device_return_type = models.CharField(max_length = 4, choices = DEVICE_RETURN_TYPE, default = 'DRSR')
    device_damage_present = models.BooleanField(default = 0)
    device_damage_dd = models.BooleanField(default = 0)
    device_damage_edd = models.BooleanField(default = 0)
    device_damage_lis = models.BooleanField(default = 0)
    device_damage_cs = models.BooleanField(default = 0)
    device_damage_tnc = models.BooleanField(default = 0)
    device_damage_tc = models.BooleanField(default = 0)
    device_damage_ms = models.BooleanField(default = 0)
    device_damage_ld = models.BooleanField(default = 0)
    device_damage_mkr = models.BooleanField(default = 0)
    device_damage_mku = models.BooleanField(default = 0)
    device_damage_bci = models.BooleanField(default = 0)
    device_damage_ccd = models.BooleanField(default = 0)
    device_bin = models.CharField(max_length = 10, null = True, blank = True)

    charger_return_type = models.CharField(max_length = 5, choices = CHARGER_RETURN_TYPE, default = 'CR')
    charger_damage_present = models.BooleanField(default = 0)
    charger_dh = models.BooleanField(default = 0)
    charger_ex = models.BooleanField(default = 0)
    charger_co = models.BooleanField(default = 0)
    charger_br = models.BooleanField(default = 0)

    class Meta:
        verbose_name = 'Device Collection'
        verbose_name_plural = 'Device Collections'

class NewDataCollection(models.Model):
    DEVICE_RETURN_TYPE = (
        ('DRSR', 'Device Returned (Summer Refresh)'),
        ('DRNR', 'Device Returned (Not Returning)')
    )

    CHARGER_RETURN_TYPE = (
        ('CR', 'Charger Returned'),
        ('CNR', 'Charger Not Returned'),
        ('CNRSR', 'Charger Not Returned (Summer Refresh)')
    )

    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4)
    device = models.ForeignKey(Device, null = True, on_delete = models.SET_NULL)
    student = models.ForeignKey(StudentModel, null = True, on_delete = models.SET_NULL)

    created = models.DateTimeField(auto_now_add = True, null = True)
    updated = models.DateTimeField(auto_now = True, null = True)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)

    student_next_location = models.ForeignKey(Location, null = True, blank = True, on_delete = models.SET_NULL)
    student_next_grade = models.CharField(max_length = 2, null = True, blank = True)

    parent_address = models.CharField(max_length = 150, null = True)
    parent_email = models.EmailField(null = True)
    parent_name = models.CharField(max_length = 50, null = True)
    parent_phone = models.CharField(max_length = 15, null = True)

    device_return_type = models.CharField(max_length = 4, choices = DEVICE_RETURN_TYPE, default = 'DRSR')
    device_damage_present = models.BooleanField(default = 0)
    device_damage_dd = models.BooleanField(default = 0)
    device_damage_edd = models.BooleanField(default = 0)
    device_damage_lis = models.BooleanField(default = 0)
    device_damage_cs = models.BooleanField(default = 0)
    device_damage_tnc = models.BooleanField(default = 0)
    device_damage_tc = models.BooleanField(default = 0)
    device_damage_ms = models.BooleanField(default = 0)
    device_damage_ld = models.BooleanField(default = 0)
    device_damage_mkr = models.BooleanField(default = 0)
    device_damage_mku = models.BooleanField(default = 0)
    device_damage_bci = models.BooleanField(default = 0)
    device_damage_ccd = models.BooleanField(default = 0)
    device_bin = models.CharField(max_length = 10, null = True, blank = True)

    charger_return_type = models.CharField(max_length = 5, choices = CHARGER_RETURN_TYPE, default = 'CR')
    charger_damage_present = models.BooleanField(default = 0)
    charger_dh = models.BooleanField(default = 0)
    charger_ex = models.BooleanField(default = 0)
    charger_co = models.BooleanField(default = 0)
    charger_br = models.BooleanField(default = 0)

    class Meta:
        verbose_name = 'Device Collection'
        verbose_name_plural = 'Device Collections'

class DataDistributionArchive(models.Model):
    id = models.CharField(max_length = 40, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    student_id = models.CharField(max_length = 15, verbose_name = 'ID')

    created = models.DateTimeField(auto_now_add = True, null = True)
    updated = models.DateTimeField(auto_now = True, null = True)

    student_first_name = models.CharField(max_length = 25, null = True)
    student_grade = models.CharField(max_length = 2, null = True)
    student_last_name = models.CharField(max_length = 25, null = True)
    student_location = models.ForeignKey(Location, null = True, on_delete = models.SET_NULL)

    parent_address = models.CharField(max_length = 150, null = True)
    parent_agreement = models.BooleanField()
    parent_email = models.EmailField(null = True)
    parent_name = models.CharField(max_length = 50, null = True)
    parent_phone = models.CharField(max_length = 15, null = True)
    parent_signature = models.CharField(max_length = 75, null = True)

    payment_amount = models.DecimalField(max_digits = 6, decimal_places = 2, null = True)
    payment_complete = models.BooleanField(default = 0)

    promotion_code = models.CharField(max_length = 25, null = True, blank = True)

    class Meta:
        ordering = ['student_id', 'student_first_name', 'student_last_name']
        verbose_name = 'Distribution Data'
        verbose_name_plural = 'Distribution Data'

    def __str__(self):
        return self.student_id

class DataDistribution(models.Model):
    student_id = models.CharField(max_length = 15, primary_key = True, unique = True, verbose_name = 'ID')

    created = models.DateTimeField(auto_now_add = True, null = True)
    updated = models.DateTimeField(auto_now = True, null = True)

    student_first_name = models.CharField(max_length = 25, null = True)
    student_grade = models.CharField(max_length = 2, null = True)
    student_last_name = models.CharField(max_length = 25, null = True)
    student_location = models.ForeignKey(Location, null = True, on_delete = models.SET_NULL)

    parent_address = models.CharField(max_length = 150, null = True)
    parent_agreement = models.BooleanField()
    parent_email = models.EmailField(null = True)
    parent_name = models.CharField(max_length = 50, null = True)
    parent_phone = models.CharField(max_length = 15, null = True)
    parent_signature = models.CharField(max_length = 75, null = True)

    payment_amount = models.DecimalField(max_digits = 6, decimal_places = 2, null = True)
    payment_complete = models.BooleanField(default = 0)

    promotion_code = models.CharField(max_length = 25, null = True, blank = True)

    class Meta:
        ordering = ['student_id', 'student_first_name', 'student_last_name']
        verbose_name = 'Distribution Data'
        verbose_name_plural = 'Distribution Data'

    def __str__(self):
        return self.student_id

    def form_completed(self):
        if int(self.updated.strftime('%Y')) >= 2020:
            return True
        else:
            return False

    def payment_completed(self):
        if self.payment_complete == 1:
            return True
        else:
            return False

    def get_parent_firstname(self):
        return self.parent_name.split(' ')[0]

    def get_parent_lastname(self):
        return self.parent_name.split(' ')[-1]

class DataSchoolPay(models.Model):
    id = models.CharField(max_length = 40, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    student_id = models.CharField(max_length = 256)

    timestamp = models.CharField(max_length = 256)
    author = models.CharField(max_length = 256, null = True)
    description = models.CharField(max_length = 256)
    amount = models.CharField(max_length = 256)
    paid = models.CharField(max_length = 256)

    payer_name = models.CharField(max_length = 256)
    payer_email = models.CharField(max_length = 256)

    class Meta:
        verbose_name = 'SchoolPay Data'
        verbose_name_plural = 'SchoolPay Data'

    def __str__(self):
        return str(self.id)

class L5QDistribution(models.Model):
    ISSUE_TYPES = (
        ('R', 'Registration'),
        ('ND', 'New Device'),
        ('NI', 'No Issue'),
        ('NS', 'New Student'),
        ('O', 'Other')
    )

    id = models.CharField(max_length = 40, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    student = models.ForeignKey(StudentModel, on_delete = models.CASCADE)

    created = models.DateTimeField(auto_now_add = True, null = True)
    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)
    updated = models.DateTimeField(auto_now = True, null = True)
    completed = models.BooleanField(default = 0)
    tech_required = models.BooleanField(default = 0)
    tech_completed = models.BooleanField(default = 0)

    issue_type = models.CharField(max_length = 2, choices = ISSUE_TYPES, null = True, blank = True)
    vehicle_description = models.CharField(max_length = 75, null = True, blank = True)
    iiq_ticket = models.CharField(max_length = 100, null = True, blank = True)
    iiq_ticket_number = models.CharField(max_length = 25, null = True, blank = True)

    class Meta:
        verbose_name = 'L5 Queue Data'
        verbose_name_plural = 'L5 Queue Data'

    def __str__(self):
        return str(self.id)

    def get_ready_status(self):
        if self.completed == 1:
            return 'complete'
        else:
            if self.tech_required == 1 and self.tech_completed == 0:
                return 'tech_working'
            elif self.tech_required == 1 and self.tech_completed == 1:
                student_data_exists = DataDistribution.objects.filter(student_id = self.student.id, updated__gte = '').exists()

                if student_data_exists:
                    student_data = DataDistribution.objects.get(student_id = self.student.id)

                    if student_data.form_completed() and student_data.payment_completed():
                        return 'ready'
                    else:
                        return 'form_needed'
                else:
                    return 'form_needed'
            elif self.tech_required == 0:
                student_data_exists = DataDistribution.objects.filter(student_id = self.student.id).exists()

                if student_data_exists:
                    student_data = DataDistribution.objects.get(student_id = self.student.id)

                    if student_data.form_completed() and student_data.payment_completed():
                        return 'ready'
                    else:
                        return 'form_needed'
                else:
                    return 'form_needed'

    def get_wait_time(self):
        startdelta = datetime.timedelta(hours = self.created.hour, minutes = self.created.minute, seconds = self.created.second)
        enddelta = datetime.timedelta(hours = datetime.datetime.now().hour, minutes = datetime.datetime.now().minute, seconds = datetime.datetime.now().second)
        return (enddelta - startdelta)

class ContactValidation(models.Model):
    parent_name = models.CharField(max_length = 50)
    parent_email = models.CharField(max_length = 50)
    parent_phone = models.CharField(max_length = 15)
    parent_id_state = models.CharField(max_length = 2)
    parent_id_number = models.CharField(max_length = 30)
    student_id = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)


class EmergencyContactInfo(models.Model):
    student_id = models.CharField(max_length=10)
    fam_1_parent_1_name = models.CharField(max_length=50)
    fam_1_parent_1_cell_phone = models.CharField(max_length=15)
    fam_1_parent_1_daytime_phone = models.CharField(max_length=15)
    fam_1_parent_2_name = models.CharField(max_length=50)
    fam_1_parent_2_cell_phone = models.CharField(max_length=15)
    fam_1_parent_2_daytime_phone = models.CharField(max_length=15)
    fam_1_parent_1_email = models.CharField(max_length=50)
    fam_1_parent_2_email = models.CharField(max_length=50)
    fam_1_residence = models.CharField(max_length=256)
    fam_1_mailing = models.CharField(max_length=256)
    fam_2_parent_1_name = models.CharField(max_length=50)
    fam_2_parent_1_cell_phone = models.CharField(max_length=15)
    fam_2_parent_1_daytime_phone = models.CharField(max_length=15)
    fam_2_parent_2_name = models.CharField(max_length=50)
    fam_2_parent_2_cell_phone = models.CharField(max_length=15)
    fam_2_parent_2_daytime_phone = models.CharField(max_length=15)
    fam_2_email = models.CharField(max_length=50)
    fam_2_residence = models.CharField(max_length=256)
    fam_2_mailing = models.CharField(max_length=256)
    custody_paperwork = models.CharField(max_length=7)
    pickup_5_name = models.CharField(max_length=50)
    pickup_5_phone = models.CharField(max_length=15)
    pickup_5_relationship = models.CharField(max_length=20)
    pickup_6_name = models.CharField(max_length=50)
    pickup_6_phone = models.CharField(max_length=15)
    pickup_6_relationship = models.CharField(max_length=20)
    pickup_7_name = models.CharField(max_length=50)
    pickup_7_phone = models.CharField(max_length=15)
    pickup_7_relationship = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class MedicalNeeds(models.Model):
    student_id = models.CharField(max_length=10)
    allergies = models.CharField(max_length=7)
    allergic_to = models.CharField(max_length=256)
    glasses_or_contacts = models.CharField(max_length=7)
    hearing_aids = models.CharField(max_length=7)
    physician_name = models.CharField(max_length=50)
    physician_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)


class SchoolClinicServices(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.CharField(max_length=10)
    basic_first_aid = models.CharField(max_length=7)
    minor_wound_care = models.CharField(max_length=7)
    minor_eye_irritation = models.CharField(max_length=7)
    minor_bites_and_stings = models.CharField(max_length=7)
    minor_upset_stomach = models.CharField(max_length=7)
    check_for_rashes = models.CharField(max_length=7)
    clinic_services_electronic_signature = models.CharField(max_length=50)
    clinic_services_checkbox = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)


class MediaParentChoice(models.Model):
    student_id = models.CharField(max_length=10)
    media_choice_level = models.CharField(max_length=1)
    media_choice_electronic_signature = models.CharField(max_length=50)
    media_choice_checkbox = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
