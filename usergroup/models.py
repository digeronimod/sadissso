from django.contrib.auth.models import Group, User
from django.db import models

class UserGroup(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)

        if created:
            viewer_group = Group.objects.get(name='Viewer')
            self.user.groups.add(viewer_group)

    class Meta:
        verbose_name = 'User Group'
        verbose_name_plural = 'User Groups'
