# Django
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
# Application
from . import ajax, views

app_name = 'reports'

urlpatterns = [
    path('', views.home, name = 'home'),
    #path('reports/media_parent_choice', views.reports, name = 'media_parent_reports')
    # Distributions
    path('distributions/overview/', views.distributions_overview, name = 'distributions_overview'),
    path('distributions/calendly/', views.distributions_calendly, name = 'distributions_calendly'),
    # Users
    path('users/temporary_ids/', views.temporary_ids, name = 'temporary_ids'),
    path('users/case_inventory/', views.case_inventory, name = 'case_inventory'),
    # Devices
    path('devices/assignments/', views.device_assignments, name = 'device_assignments'),
    path('devices/lauper/', views.lauper_data, name = 'lauper_data'),
    path('devices/devito/', views.devito_data, name = 'devito_data'),
    path('devices/historical/', views.device_history, name = 'device_history'),
    path('devices/inactive/', views.device_inactive, name = 'device_inactive'),
    path('devices/delinquent/', views.device_delinquent, name = 'device_delinquent'),
    path('devices/bins/', views.device_bins, name = 'device_bins'),
    path('export/', views.export_csv, name = 'export_csv'),
    # Summer
    path('summer/enrolled/', views.summer_enrolled, name = 'summer_enrolled'),
    # Collections
    path('collections/overview/', views.collections_overview, name = 'collections_overview'),
    path('collections/export_collections_detail/', views.export_collections_detail, name = 'export_collections_detail'),
    # AJAX
    path('export/district/signups/', ajax.export_distributions_signups, name = 'export_distributions_signups'),
    path('export/district/devices/', ajax.export_distributions_devices, name = 'export_distributions_devices'),
    path('export/district/staging/', ajax.export_staging_data, name = 'export_staging_data'),
    path('export/district/student_devices/', ajax.export_student_devices, name = 'export_student_devices'),
    path('export/district/student_devices_full/', ajax.export_student_devices_full, name = 'export_student_devices_full'),
    path('export/summer/enrollment/', ajax.export_student_enrollment, name = 'export_student_enrollment'),
    path('export/user/case_assignment/', ajax.export_case_assignments, name = 'export_case_assignments'),
    path('export/user/temporary_ids/', ajax.export_temporary_ids, name = 'export_temporary_ids'),
    # Progress
    path('task/', ajax.get_progress_state, name = 'get_progress_state')
]

if settings.DEBUG:
    urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
