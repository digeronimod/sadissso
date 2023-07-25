from django.urls import path

from . import views as user_views

urlpatterns = [
    path('users/', user_views.UsersListCreateAPIView.as_view(), name = 'api-users-list'),
    path('users/<int:pk>/', user_views.UsersDetailsAPIView.as_view(), name = 'api-user-details'),
    path('students/', user_views.StudentListCreateAPIView.as_view(), name = 'api-students-list'),
    path('students/<int:pk>/', user_views.StudentDetailsAPIView.as_view(), name = 'api-student-details')
]
