# Django
from django.contrib import admin
# Application
from .models import DistributionLane, DistributionQueue, DistributionStatus

@admin.register(DistributionLane)
class DistributionLaneAdmin(admin.ModelAdmin):
    list_display = ['id', 'alias', 'name', 'get_members', 'trouble']
    ordering = ['alias']
    search_fields = ['members__username']

    def get_members(self, object):
        return "\n".join([f'{member.first_name} {member.last_name}' for member in object.members.all()])

@admin.register(DistributionQueue)
class DistributionQueueAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'created', 'updated', 'claimed', 'found', 'assigned', 'author', 'claimer', 'status', 'lane', 'bpi', 'bin']
    ordering = ['student']
    search_fields = ['student', 'bin', 'bpi']
    autocomplete_fields = ['student', 'author', 'claimer', 'bpi']

@admin.register(DistributionStatus)
class DistributionStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'alias', 'name']
    ordering = ['alias']
