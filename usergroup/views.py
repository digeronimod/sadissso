from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import Group

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(auth_views.LoginView):
    def form_valid(self, form):
        """Override form_valid method to assign user to 'Viewer' group."""
        response = super().form_valid(form)
        group, _ = Group.objects.get_or_create(name='Viewer')
        self.request.user.groups.add(group)
        return response
