# Django
from django.urls import path
# Application
from . import ajax, views

app_name = 'assets'

urlpatterns = [
    path('', views.home, name = 'home'),
    path('<str:id>/', views.detail, name = 'detail'),
    # AJAX Requests
    path('ajax/update_device_bin/', ajax.update_device_bin, name = 'update_device_bin')
]
