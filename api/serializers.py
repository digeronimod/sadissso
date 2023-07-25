# Django
from django.contrib.auth.models import User
# Plugins
from rest_framework import serializers
# Application
from users.models import StudentModel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'first_name', 'last_name', 'groups']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentModel
        fields = ['id', 'iiq_id', 'name', 'username', 'location', 'type', 'is_remote', 'status', 'foreign_status', 'birthdate']
