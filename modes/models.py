# Python
import uuid
# Django
from django.contrib.auth.models import User
from django.db import models
# Application
from inventory.models import Device
from users.models import Student

class DistributionLane(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    alias = models.CharField(max_length = 10, null = True)
    name = models.CharField(max_length = 30, null = True)
    members = models.ManyToManyField(User, blank = True)
    trouble = models.BooleanField(default = 0)

    class Meta:
        verbose_name = 'Distribution Lane'
        verbose_name_plural = 'Distribution Lanes'

    def __str__(self):
        return self.name

class DistributionStatus(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    alias = models.CharField(max_length = 10, null = True)
    name = models.CharField(max_length = 30, null = True)

    class Meta:
        verbose_name = 'Distribution Status'
        verbose_name_plural = 'Distribution Statuses'

    def __str__(self):
        return self.name

class DistributionQueue(models.Model):
    id = models.CharField(max_length = 36, primary_key = True, unique = True, default = uuid.uuid4, editable = False)
    student = models.ForeignKey(Student, null = True, on_delete = models.SET_NULL)

    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    claimed = models.DateTimeField(null = True, blank = True)
    found = models.DateTimeField(null = True, blank = True)
    assigned = models.DateTimeField(null = True, blank = True)

    author = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'dqueue_author')
    claimer = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'dqueue_claimer')
    status = models.ForeignKey(DistributionStatus, null = True, on_delete = models.SET_NULL)

    lane = models.ForeignKey(DistributionLane, null = True, on_delete = models.SET_NULL)
    bpi = models.ForeignKey(Device, null = True, on_delete = models.SET_NULL)
    bin = models.CharField(max_length = 10)

    class Meta:
        verbose_name = 'Distribution Queue'
        verbose_name_plural = 'Distribution Queue'

    def __str__(self):
        return f'{self.student.id}: {self.bpi} ({self.bin})'
