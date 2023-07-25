# Python
import os
from celery import Celery
# Django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sadis.settings')

app = Celery('sadis')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind = True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
