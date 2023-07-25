# Framework
from django.urls import path
# Application
from . import views

app_name = 'modes'

urlpatterns = [
    path('distributions/', views.distributions, name = 'distributions'),
    path('distributions/runner/', views.distributions_runner, name = 'distributions_runner')
]
