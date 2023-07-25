from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from usergroup.backends import assign_viewer_group

User = get_user_model()

@receiver(post_save, sender=User)
def add_user_to_viewer_group(sender, instance, created, **kwargs):
    if created:
        assign_viewer_group(sender, instance, None)
