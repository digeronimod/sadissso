# Django
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
# SADIS
from . import ajax, views
from dlmr import views as dlmr_views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name = 'home'),
    path('changelog/', views.changelog, name = 'changelog'),
    path('scl/', views.scl, name = 'scl'),
    # Compatibility
    path('dlm/registration/', dlmr_views.dlm_registration, name = 'dlm_registration'),
    # Internal Forms
    path('tools/devices/expiration/', views.summer_program, name = 'expiration_extension'),
    # POST Requests
    path('calendly/', views.calendly_appointment, name = 'calendly_appointment'),
    # AJAX Requests
    path('ajax/collections_bin_change/', ajax.collections_bin_change, name='collections_bin_change')
]

if settings.DEBUG:
    urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
