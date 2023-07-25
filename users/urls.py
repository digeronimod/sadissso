from django.urls import path
from . import ajax, views

app_name = 'users'

urlpatterns = [
    # Base
    path('', views.home, name = 'home'),
    path('students/', views.home_students, name = 'home_students'),
    path('students/', views.home_students, name = 'detail_students'),
     path('students/', views.home_students, name = 'detail_students2'),
    path('employees/', views.home_employees, name = 'home_employees'),
    path('collections/', views.collections, name = 'collections'),
    path('distributions/', views.distributions, name = 'distributions'),
    path('distributions/l5q/', views.distributions_l5q, name = 'distributions_l5q'),
    path('distributions/sq/', views.distributions_sq, name = 'distributions_sq'),
    path('distributions/tq/', views.distributions_tq, name = 'distributions_tq'),
    # path('<str:id>/', views.detail, name = 'detail'),
    path('students/<str:id>/', views.detail_students, name = 'detail_students'),
    # path('employees/<str:id>/', views.detail_employees, name = 'detail_employees'),
    # AJAX Requests
    path('ajax/add_alert/', ajax.add_alert, name = 'add_alert'),
    path('ajax/add_id_log/', ajax.add_id_print_log, name = 'add_id_log'),
    path('ajax/add_note/', ajax.add_note, name = 'add_note'),
    path('ajax/add_fine/', ajax.add_fine, name = 'add_fine'),
    path('ajax/add_device_submit/', ajax.add_device_submit, name = 'add_device_submit'),
    path('ajax/archive_dlmr_data/', ajax.archive_dlmr_data, name = 'archive_dlmr_data'),
    path('ajax/get_device/', ajax.get_device, name = 'get_device'),
    path('ajax/modify_device_submit/', ajax.modify_device_submit, name = 'modify_device_submit'),
    path('ajax/add_charger_submit/', ajax.add_charger_submit, name = 'add_charger_submit'),
    path('ajax/get_charger/', ajax.get_charger, name = 'get_charger'),
    path('ajax/modify_charger_submit/', ajax.modify_charger_submit, name = 'modify_charger_submit'),
    path('ajax/update_student_password/', ajax.update_student_password, name = 'update_student_password'),
    path('ajax/update_staging_data/', ajax.update_staging_data, name = 'update_staging_data'),
    path('ajax/collect_device/', ajax.collect_device, name = 'collect_device'),
    path('ajax/collect_device_submit/', ajax.collect_device_submit, name = 'collect_device_submit'),
    path('contact_validation_submit/', views.contact_validation, name = 'submit_contact_validation'),
    path('emergency_contact_info/', views.emergency_contact_info, name = 'emergency_contact_info'),
    path('users/medical_needs/', views.medical_needs, name = 'medical_needs'),
    path('users/school_clinic_services/', views.school_clinic_services, name = 'school_clinic_services'),
    path('users/media_parent_choice/', views.media_parent_choice, name='media_parent_choice'),
    # Tests
    path('<str:id>/email/device_receipt/', views.device_receipt, name='device_receipt')
]
