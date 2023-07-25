from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def assign_group_to_user(sender, user, request, **kwargs):
    # Check if the user logged in via allauth
    if user.backend == 'allauth.account.auth_backends.AuthenticationBackend':
        # Retrieve or create the desired group
        group, created = Group.objects.get_or_create(name='Viewer')

        # Assign the user to the group
        user.groups.add(group)
