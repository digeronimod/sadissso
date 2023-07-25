# Django
from django.urls import path
# SADIS
from . import views

app_name = 'dlmr'

urlpatterns = [
    path('', views.dlm_registration, name = 'dlm_registration'),
    path('success/', views.dlm_registration_success, name = 'dlm_registration_success'),
    path('users/contact_validation_submit/', views.contact_validation, name = 'contact_validation_submit'),
    path('users/emergency_contact_info/', views.emergency_contact_info, name = 'emergency_contact_info'),
    path('users/medical_needs/', views.medical_needs, name = 'medical_needs'),
    path('users/school_clinic_services/', views.school_clinic_services, name = 'school_clinic_services'),
    path('users/media_parent_choice/', views.media_parent_choice, name='media_parent_choice')

]
