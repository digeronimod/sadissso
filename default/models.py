# Python
import datetime, uuid
from distutils.util import strtobool
# Django
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
# Plugins
from multiselectfield import MultiSelectField
from simple_history.models import HistoricalRecords
# SADIS
from sadis.api import api_iiq as iiq

class Location(models.Model):
    LOCATION_TYPES = (
        ('E', 'Elementary'),
        ('G', 'Government'),
        ('O', 'Other'),
        ('S', 'Secondary'),
        ('V', 'Virtual')
    )

    id = models.CharField(max_length = 5, primary_key = True, unique = True, verbose_name = 'ID')
    iiq_id = models.UUIDField(blank = True, null = True)
    name = models.CharField(max_length = 30)
    type = models.CharField(max_length = 1, choices = LOCATION_TYPES, default = 'O')
    alias = models.CharField(max_length = 10, null = True, blank = True)
    team_id = models.UUIDField(blank = True, null = True)
    msb_store = models.CharField(max_length = 10, null = True, verbose_name = 'MSB Store ID')
    msb_glaccount = models.CharField(max_length = 30, null = True, verbose_name = 'MSB G/L Account')

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.name

class LocationCode(models.Model):
    id = models.CharField(max_length = 5, primary_key = True, unique = True, verbose_name = 'ID')
    name = models.CharField(max_length = 50)

    class Meta:
        ordering = ['id']
        verbose_name = 'Location Code'
        verbose_name_plural = 'Location Codes'

    def __str__(self):
        return self.name

class FineTypes(models.Model):
    alias = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 100)
    value = models.DecimalField(max_digits = 6, decimal_places = 2, null = True, blank = True)

    class Meta:
        verbose_name = 'Fine Type'
        verbose_name_plural = 'Fine Types'

    def __str__(self):
        return self.name

class FineSubtypes(models.Model):
    DEVICE_TYPE_CHOICES = (
        ('U', 'Universal'),
        ('MB', 'MacBook'),
        ('IP', 'iPad'),
        ('HS', 'HotSpot')
    )

    alias = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 100)
    value = models.DecimalField(max_digits = 6, decimal_places = 2)
    flexible = models.BooleanField(default = False)
    device_type = MultiSelectField(max_length = 50, choices = DEVICE_TYPE_CHOICES, default = 'U')

    class Meta:
        verbose_name = 'Fine Subtype'
        verbose_name_plural = 'Fine Subtypes'

    def __str__(self):
        return self.name

class Person(models.Model):
    PERSON_TYPES = (
        ('F', 'Staff'),
        ('S', 'Student'),
        ('N', 'None')
    )

    id = models.CharField(max_length = 15, primary_key = True, unique = True, verbose_name = 'ID')
    iiq_id = models.UUIDField(null = True, blank = True)
    name = models.CharField(max_length = 50)
    username = models.CharField(max_length = 30, unique = True)
    location = models.ForeignKey(Location, null = True, on_delete = models.SET_NULL)
    type = models.CharField(max_length = 1, choices = PERSON_TYPES, default = 'N')
    is_remote = models.BooleanField(default = 0)
    iiq_updated = models.DateTimeField(default = datetime.datetime(1800, 1, 1, 0, 0, 0), verbose_name = 'IIQ Updated')
    mosyle_updated = models.DateTimeField(default = datetime.datetime(1800, 1, 1, 0, 0, 0), verbose_name = 'Mosyle Updated')
    sadis_updated = models.DateTimeField(auto_now = True, verbose_name = 'SADIS Updated')
    status = models.BooleanField(default = 0)
    foreign_status = models.ForeignKey('PersonStatuses', null = True, on_delete = models.SET_NULL)
    birthdate = models.DateField(null = True, blank = True)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    def get_status(self):
        if self.status:
            return 'Yes'
        else:
            return 'No'

    class Meta:
        ordering = ['id', 'name']
        verbose_name_plural = 'People'

    def __str__(self):
        return self.name

class PersonTypes(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Person Type'
        verbose_name_plural = 'Person Types'

    def __str__(self):
        return self.name

class PersonStatuses(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Person Status'
        verbose_name_plural = 'Person Statuses'

    def __str__(self):
        return self.name

class PersonPrograms(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 100, null = True, blank = True)

    begin = models.DateTimeField(default = datetime.datetime(1980, 1, 1, 8, 0, 0), verbose_name = 'Begin Date')
    expiration = models.DateTimeField(default = datetime.datetime(1980, 1, 1, 8, 0, 0), verbose_name = 'Expiration Date')

    class Meta:
        verbose_name = 'Summer Program'
        verbose_name_plural = 'Summer Programs'

    def __str__(self):
        return self.name

class Device(models.Model):
    DEVICE_STATUS = (
        ('AS', 'Storage'),
        ('BR', 'Broken'),
        ('IS', 'In Service'),
        ('MI', 'Missing'),
        ('RE', 'Retired'),
        ('SD', 'Sold'),
        ('ST', 'Stolen')
    )

    id = models.CharField(max_length = 10, primary_key = True, unique = True, verbose_name = 'ID')
    iiq_id = models.CharField(max_length = 40, null = True, blank = True)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    status = models.CharField(max_length = 2, choices = DEVICE_STATUS, default = 'IS')
    foreign_status = models.ForeignKey('DeviceStatuses', default = 'A', null = True, on_delete = models.SET_NULL)
    manufacturer = models.CharField(max_length = 25, null = True, blank = True)
    model = models.CharField(max_length = 50, null = True, blank = True)
    foreign_model = models.ForeignKey('DeviceModel', null = True, blank = True, on_delete = models.SET_NULL)
    serial = models.CharField(max_length = 20)
    location = models.ForeignKey(Location, null = True, blank = True, on_delete = models.SET_NULL)
    bin = models.CharField(max_length = 10, null = True, blank = True)
    has_case = models.BooleanField(default = False)
    owner = models.ForeignKey(Person, null = True, blank = True, on_delete = models.SET_NULL)
    owner_assign_date = models.DateTimeField(null = True, blank = True)
    owner_assign_author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)
    role = models.ManyToManyField('DeviceRole', through = 'DeviceAssignment')

    iiq_updated = models.DateTimeField(default = datetime.datetime(1800, 1, 1, 0, 0, 0), verbose_name = 'IIQ Updated')
    mosyle_updated = models.DateTimeField(default = datetime.datetime(1800, 1, 1, 0, 0, 0), verbose_name = 'Mosyle Updated')
    munki_updated = models.DateTimeField(default = datetime.datetime(1800, 1, 1, 0, 0, 0), verbose_name = 'Munki Updated')
    sadis_updated = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ['id', 'manufacturer', 'model']
        verbose_name_plural = 'Devices'

    def __str__(self):
        return (f'{self.manufacturer} {self.model}')

    def set_iiq_id(self):
        if not self.iiq_id:
            self.iiq_id = iiq.get_asset_uuid(self.id)

            self.save()

    def set_owner(self, user_object, request_object):
        if not self.iiq_id:
            self.iiq_id = iiq.get_asset_uuid(self.id)

        api_response = iiq.assign_asset_to_user(self.iiq_id, user_object.iiq_id)

        if api_response.status_code == 200:
            self.owner = user_object
            self.location = user_object.location
            self.owner_assign_date = timezone.now()
            self.owner_assign_author = request_object

            self.save()

            return True
        else:
            return False

    def set_owner_by_force(self, user_object, request_object):
        if not self.iiq_id:
            self.iiq_id = iiq.get_asset_uuid(self.id)

        if not user_object.iiq_id:
            student_uuid = iiq.get_user_uuid(user_object.id)
        else:
            student_uuid = user_object.iiq_id

        api_response = iiq.assign_asset_to_user_by_force(self.iiq_id, student_uuid)

        if api_response.status_code == 200:
            if self.owner != user_object:
                self.owner = user_object
                self.location = user_object.location
                self.owner_assign_date = timezone.now()
                self.owner_assign_author = request_object

                self.save()

    def set_owner_without_iiq(self, user_object, request_object):
        if self.owner != user_object:
            self.owner = user_object
            self.location = user_object.location
            self.owner_assign_date = timezone.now()
            self.owner_assign_author = request_object

            self.save()

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True

        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving

        return ret

    def delete_owner(self, request_object):
        if not self.iiq_id:
            self.iiq_id = iiq.get_asset_uuid(self.id)

        api_response = iiq.unassign_asset(self.id)

        if api_response.status_code == 200:
            if self.owner != None:
                self.owner = None
                self.owner_assign_date = timezone.now()
                self.owner_assign_author = request_object

                self.save_without_historical_record()

class DeviceRole(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Device Role'
        verbose_name_plural = 'Device Roles'

    def __str__(self):
        return self.name

class DeviceStatuses(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Device Status'
        verbose_name_plural = 'Device Statuses'

    def __str__(self):
        return self.name

class DeviceAssignment(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4)

    device = models.ForeignKey(Device, on_delete = models.CASCADE)
    role = models.ForeignKey(DeviceRole, null = True, on_delete = models.SET_NULL)

    class Meta:
        verbose_name = 'Device Assignment'
        verbose_name_plural = 'Device Assignments'

class DeviceModel(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)
    charger = models.ForeignKey("ChargerType", null = True, blank = True, on_delete = models.SET_NULL)

    class Meta:
        verbose_name = 'Device Model'
        verbose_name_plural = 'Device Models'

    def __str__(self):
        return self.name

class DeviceAssessment(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    device = models.ForeignKey(Device, null = True, on_delete = models.SET_NULL)
    author = models.ForeignKey(User, null = True, on_delete = models.SET_NULL)
    created = models.DateTimeField(auto_now_add = True)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    device_damage_present = models.BooleanField(default = 0)
    device_damage_dd = models.BooleanField(default = 0)
    device_damage_edd = models.BooleanField(default = 0)
    device_damage_lis = models.BooleanField(default = 0)
    device_damage_cs = models.BooleanField(default = 0)
    device_damage_tnc = models.BooleanField(default = 0)
    device_damage_tc = models.BooleanField(default = 0)
    device_damage_prt = models.BooleanField(default = 0)
    device_damage_ms = models.BooleanField(default = 0)
    device_damage_ld = models.BooleanField(default = 0)
    device_damage_mkr = models.BooleanField(default = 0)
    device_damage_mku = models.BooleanField(default = 0)
    device_damage_bci = models.BooleanField(default = 0)
    device_damage_ccd = models.BooleanField(default = 0)

class Note(models.Model):
    id = models.AutoField(primary_key = True, unique = True)
    item_id = models.CharField(max_length = 25)

    attached_id = models.CharField(max_length = 36, null = True, blank = True)
    author = models.ForeignKey(User, null = True, on_delete = models.SET_NULL)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    history = HistoricalRecords(history_change_reason_field = models.TextField(null = True))

    class Meta:
        ordering = ['item_id', 'id']

    def __str__(self):
        return self.body

class Charger(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)

    type = models.ForeignKey('ChargerType', default = 'PROP', null = True, on_delete = models.SET_NULL)
    status = models.ForeignKey('ChargerCondition', default = 'N', null = True, on_delete = models.SET_NULL)
    owner = models.ForeignKey(Person, null = True, blank = True, on_delete = models.SET_NULL)
    owner_assign_date = models.DateTimeField(null = True, blank = True)
    owner_assign_author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)

    location = models.ForeignKey(Location, null = True, blank = True, on_delete = models.SET_NULL)
    bin = models.CharField(max_length = 10, null = True, blank = True)
    adapter = models.BooleanField(default = 1)
    cord = models.BooleanField(default = 1)

    class Meta:
        verbose_name = 'Peripheral'
        verbose_name_plural = 'Peripherals'

    def __str__(self):
        return str(self.type)

    def assign_owner(self, user_object, request_object):
        self.owner = user_object
        self.owner_assign_date = timezone.now()
        self.owner_assign_author = request_object
        self.bin = None

        self.save()

    def delete_owner(self, request_object):
        if self.owner != None:
            self.owner = None
            self.owner_assign_date = timezone.now()
            self.owner_assign_author = request_object

            self.save()

    def modify_parts(self, adapter, cord):
        if bool(self.adapter) != adapter or bool(self.cord) != cord:
            if bool(self.adapter) != adapter:
                self.adapter = adapter

            if bool(self.cord) != cord:
                self.cord = cord

            self.save()

class ChargerCondition(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)

    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Peripheral Condition'
        verbose_name_plural = 'Peripheral Conditions'

    def __str__(self):
        return self.name

class ChargerType(models.Model):
    id = models.CharField(max_length = 10, primary_key = True, unique = True)
    name = models.CharField(max_length = 50)

    brick_fine = models.ForeignKey(FineSubtypes, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'brick_fine')
    cable_fine = models.ForeignKey(FineSubtypes, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'cable_fine')
    combined_fine = models.ForeignKey(FineSubtypes, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'combined_fine')

    class Meta:
        verbose_name = 'Peripheral Type'
        verbose_name_plural = 'Peripheral Types'

    def __str__(self):
        return self.name

class CalendlyAppointment(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    data = models.JSONField(null = True)

class CalendlyEvent(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    event_id = models.CharField(max_length = 36, unique = True, null = False, blank = False)
    event_name = models.CharField(max_length = 100, null = True, blank = False)
    event_start = models.DateTimeField(null = True, blank = False)
    event_end = models.DateTimeField(null = True, blank = False)

class DeviceHistoryData(models.Model):
    id = models.UUIDField(primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    device_id = models.CharField(max_length = 50, null = True, blank = True)
    owner_id = models.CharField(max_length = 50, null = True, blank = True)
    owner_name = models.CharField(max_length = 75, null = True, blank = True)
    author_id = models.CharField(max_length = 50, null = True, blank = True)
    author_username = models.CharField(max_length = 50, null = True, blank = True)
    author_name = models.CharField(max_length = 50, null = True, blank = True)
    assign_type = models.CharField(max_length = 50, null = True, blank = True)
    assign_date = models.DateTimeField(null = True, blank = True)
