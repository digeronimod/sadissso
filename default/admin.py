# Django
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
# Plugins
from import_export.admin import ImportExportModelAdmin
# SADIS
from .models import Charger, ChargerCondition, ChargerType, Device, DeviceModel, DeviceRole, DeviceAssignment, DeviceStatuses, FineTypes, FineSubtypes, Location, LocationCode, Note, Person, PersonStatuses, PersonPrograms, PersonTypes

class ChargerOwnedFilter(SimpleListFilter):
    title = 'owned'
    parameter_name = 'owner'

    def lookups(self, request, admin_model):
        return [('no', 'No'), ('yes', 'Yes')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.all()

        if self.value() == 'yes':
            return queryset.filter(owner__isnull = False)

        if self.value() == 'no':
            return queryset.filter(owner__isnull = True)

@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ['id', 'name', 'username', 'location', 'type']
    list_filter = ['type', 'location']
    ordering = ['id', 'name']
    search_fields = ['id', 'name', 'username']

@admin.register(PersonStatuses)
class PersonStatusesAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ['id', 'name']
    ordering = ['id']

@admin.register(PersonTypes)
class PersonTypesAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ['id', 'name']
    ordering = ['id']

@admin.register(PersonPrograms)
class PersonProgramsAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'description', 'expiration']
    ordering = ['id']

@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'alias', 'type', 'iiq_id', 'team_id']
    list_filter = ['type']
    ordering = ['id']
    search_fields = ['name']

@admin.register(LocationCode)
class LocationCodeAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']
    search_fields = ['name']

@admin.register(Device)
class DeviceAdmin(ImportExportModelAdmin):
    list_display = ['id', 'manufacturer', 'foreign_model', 'serial', 'owner', 'location', 'bin']
    list_filter = ['manufacturer', 'foreign_model', 'location']
    ordering = ['id', 'manufacturer']
    search_fields = ['id', 'serial', 'owner__id', 'owner__name']
    autocomplete_fields = ['owner', 'owner_assign_author']

@admin.register(DeviceRole)
class DeviceRoleAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']

@admin.register(DeviceAssignment)
class DeviceAssignmentAdmin(ImportExportModelAdmin):
    list_display = ['device', 'role']
    list_filter = ['role']
    autocomplete_fields = ['device']

@admin.register(DeviceStatuses)
class DeviceStatusesAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']

@admin.register(DeviceModel)
class DeviceModelAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'charger']
    ordering = ['id']

@admin.register(Note)
class NoteAdmin(ImportExportModelAdmin):
    list_display = ['id', 'item_id', 'attached_id', 'body', 'created']
    ordering = ['id', 'item_id']
    search_fields = ['item_id']

@admin.register(FineTypes)
class FineTypesAdmin(ImportExportModelAdmin):
    list_display = ['alias', 'name', 'description', 'value']
    ordering = ['alias']

@admin.register(FineSubtypes)
class FineSubtypesAdmin(ImportExportModelAdmin):
    list_display = ['alias', 'name', 'description', 'value', 'flexible', 'device_type']
    ordering = ['alias']

@admin.register(Charger)
class ChargerAdmin(ImportExportModelAdmin):
    list_display = ['id', 'type', 'status', 'owner', 'location', 'bin', 'adapter', 'cord']
    list_filter = ['type', 'status', ChargerOwnedFilter, 'location', 'bin']
    ordering = ['type', 'status']
    search_fields = ['id', 'owner__id', 'owner__username', 'owner__name']
    autocomplete_fields = ['owner']

@admin.register(ChargerCondition)
class ChargerConditionAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']

@admin.register(ChargerType)
class ChargerTypeAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'brick_fine', 'cable_fine', 'combined_fine']
    ordering = ['id']
