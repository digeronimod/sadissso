# Django
from django.contrib.auth.models import User
# Plugins
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# Application
from users.models import StudentModel
from api.serializers import UserSerializer, StudentSerializer

class UsersListCreateAPIView(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('last_name')

class UsersDetailsAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class StudentListCreateAPIView(ListCreateAPIView):
    serializer_class = StudentSerializer
    queryset = StudentModel.objects.all().order_by('id')

class StudentDetailsAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    queryset = StudentModel.objects.all()
