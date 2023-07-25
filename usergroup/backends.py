from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group

class GroupModelBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return user.is_active and user.groups.filter(name='Viewer').exists()

    def get_user_permissions(self, user_obj, obj=None):
        return set()

    def get_group_permissions(self, user_obj, obj=None):
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        return set()

    def get_user(self, user_id):
        return None

def assign_viewer_group(sender, user, request, **kwargs):
    group, _ = Group.objects.get_or_create(name='Viewer')
    user.groups.add(group)
