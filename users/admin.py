# Django
from django.contrib import admin
# Plugins
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter
# SADIS
from .models import *

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

    def get_queryset(self, request):
        queryset = super(StudentAdmin, self).get_queryset(request)
        return queryset.filter(type = 'S')

    list_display = ['id', 'name', 'username', 'role', 'foreign_status', 'location', 'grade']
    list_filter = ['location', 'role', 'grade', 'foreign_status']
    ordering = ['id', 'name']
    search_fields = ['id', 'name', 'username']

@admin.register(StudentModel)
class StudentModelAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'username', 'role', 'status', 'location', 'location_code_id', 'grade', 'updated']
    list_filter = ['location', 'role', 'grade', 'status']
    ordering = ['id', 'name']
    search_fields = ['id', 'name', 'username']

@admin.register(StudentModelIDLog)
class StudentModelIDLogAdmin(ImportExportModelAdmin):
    list_display = ['student', 'author', 'date', 'id']
    list_filter = ['student__location']
    ordering = ['student']
    search_fields = ['student__id', 'student__name']

@admin.register(StudentDeviceOwnership)
class StudentDeviceOwnershipAdmin(ImportExportModelAdmin):
    list_display = ['student', 'device', 'date', 'author']
    ordering = ['student']
    autocomplete_fields = ['student', 'device']

@admin.register(StudentChargerOwnership)
class StudentChargerOwnershipAdmin(ImportExportModelAdmin):
    list_display = ['student', 'charger', 'date', 'author']
    ordering = ['student']
    autocomplete_fields = ['student', 'charger']

@admin.register(StudentRole)
class StudentRole(ImportExportModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']

@admin.register(StudentStatuses)
class StudentStatusesAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']

@admin.register(StudentFines)
class StudentFinesAdmin(ImportExportModelAdmin):
    list_display = ['student_id', 'fine_type', 'fine_subtype', 'created', 'paid']
    list_filter = ['fine_type', 'fine_subtype', ('created', DateRangeFilter)]
    ordering = ['student_id']
    autocomplete_fields = ['student']

@admin.register(StudentModelPrograms)
class StudentModelProgramsAdmin(ImportExportModelAdmin):
    search_fields = ['student__name', 'student__id']
    list_display = ['id', 'student', 'program', 'created', 'author']
    ordering = ['student']
    autocomplete_fields = ['student']

@admin.register(StudentTransfers)
class StudentTransfers(ImportExportModelAdmin):
    search_fields = ['student']
    list_display = ['id', 'student', 'transfer_from', 'transfer_to', 'created', 'author']
    ordering = ['student']

@admin.register(StaffModel)
class StaffModelAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'username', 'location']
    list_filter = ['location']
    ordering = ['id', 'name']
    search_fields = ['id', 'name', 'username']

@admin.register(DataStaging)
class DataStagingAdmin(ImportExportModelAdmin):
    search_fields = ['student_id', 'device_bpi', 'device_bin']
    list_display = ['student_id', 'device_bpi', 'device_bin', 'created', 'updated']
    ordering = ['student_id']

@admin.register(DataCollection)
class DataCollectionAdmin(ImportExportModelAdmin):
    list_display = ['student', 'device', 'device_bin', 'device_return_type', 'device_damage_present', 'device_damage_dd', 'device_damage_edd', 'device_damage_lis', 'device_damage_cs', 'device_damage_tnc', 'device_damage_tc', 'device_damage_ms', 'device_damage_ld', 'device_damage_mkr', 'device_damage_mku', 'device_damage_bci', 'device_damage_ccd', 'charger_return_type', 'charger_damage_present', 'charger_dh', 'charger_ex', 'charger_co', 'charger_br']
    search_fields = ['device__id', 'device__serial', 'student__id', 'student__name']
    autocomplete_fields = ['student', 'device']

@admin.register(DataDistribution)
class DataDistributionAdmin(ImportExportModelAdmin):
    list_display = ['student_id', 'student_first_name', 'student_last_name', 'parent_name', 'created', 'updated']
    ordering = ['student_id']
    search_fields = ['student_id', 'student_first_name', 'student_last_name']

@admin.register(DataSchoolPay)
class DataSchoolPayAdmin(ImportExportModelAdmin):
    list_display = ['student_id', 'description', 'author', 'amount', 'timestamp', 'paid', 'payer_name', 'payer_email']
    ordering = ['student_id']
    search_fields = ['student_id']

@admin.register(L5QDistribution)
class L5QDistributionAdmin(ImportExportModelAdmin):
    list_display = ['student', 'completed', 'issue_type', 'author', 'tech_required', 'iiq_ticket', 'tech_completed', 'created', 'updated', 'vehicle_description']
    ordering = ['-created']
    search_fields = ['student__name', 'student__id', 'iiq_ticket']
    autocomplete_fields = ['student', 'author']

@admin.register(ContactValidation)
class ContactValidationAdmin(ImportExportModelAdmin):
    list_display = ['student_id', 'parent_name', 'parent_email', 'parent_phone', 'parent_id_state', 'parent_id_number']
    ordering = ['student_id']

@admin.register(MediaParentChoice)
class MediaParentChoiceAdmin(ImportExportModelAdmin):
    list_display = ['student_id', 'media_choice_level', 'media_choice_electronic_signature', 'media_choice_checkbox']
    ordering = ['student_id']

@admin.register(SchoolClinicServices)
class SchoolClinicServicesAdmin(ImportExportModelAdmin):
    list_display = ['student_id', 'basic_first_aid', 'minor_wound_care', 'minor_eye_irritation', 'minor_bites_and_stings', 'minor_upset_stomach', 'check_for_rashes', 'clinic_services_electronic_signature', 'clinic_services_checkbox']
    ordering = ['student_id']


@admin.register(MedicalNeeds)
class MedicalNeedsAdmin(ImportExportModelAdmin):
    list_display = ['student_id', 'allergies', 'allergic_to', 'glasses_or_contacts', 'hearing_aids', 'physician_name', 'physician_phone']
    ordering = ['student_id']

@admin.register(EmergencyContactInfo)
class EmergencyContactAdmin(ImportExportModelAdmin):
    verbose_name_plural = 'Emergency Contact Info'
    list_display = (
        'student_id',
        'get_f1p1name_alias',
        'get_f1p1email_alias',
        'get_f1p1cell_alias',
        'get_f1p1dayphone_alias',
        'get_f1p2name_alias',
        'get_f1p2email_alias',
        'get_f1p2cell_alias',
        'get_f1p2dayphone_alias',
        'fam_1_residence',
    )

    def get_f1p1name_alias(self, obj):
        return obj.fam_1_parent_1_name

    get_f1p1name_alias.short_description = 'fam1p1name'  # Set the desired alias
    
    
    def get_f1p1email_alias(self, obj):
        return obj.fam_1_parent_1_email

    get_f1p1email_alias.short_description = 'fam1p1email'  # Set the desired alias


    def get_f1p2name_alias(self, obj):
        return obj.fam_1_parent_1_name

    get_f1p2name_alias.short_description = 'fam1p2name'  # Set the desired alias
    
    
    def get_f1p2email_alias(self, obj):
        return obj.fam_1_parent_2_email

    get_f1p2email_alias.short_description = 'fam1p2email'  # Set the desired alias
    
    
    def get_f1p1cell_alias(self, obj):
        return obj.fam_1_parent_1_cell_phone

    get_f1p1cell_alias.short_description = 'fam1p1cell'  # Set the desired alias


    def get_f1p2cell_alias(self, obj):
        return obj.fam_1_parent_2_cell_phone

    get_f1p1cell_alias.short_description = 'fam1p2cell'  # Set the desired alias
    
    
    def get_f1p1dayphone_alias(self, obj):
        return obj.fam_1_parent_1_daytime_phone

    get_f1p1dayphone_alias.short_description = 'fam1p1dayphone'  # Set the desired alias

    
    def get_f1p2dayphone_alias(self, obj):
        return obj.fam_1_parent_2_daytime_phone

    get_f1p2dayphone_alias.short_description = 'fam1p2dayphone'  # Set the desired alias