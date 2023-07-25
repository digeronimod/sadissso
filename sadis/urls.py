from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from usergroup.views import LoginView
from rest_framework import routers
from usergroup.views import UserViewSet

admin.site.site_header = "SADIS Administration"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "SADIS Administration Portal"

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
 #   path('home/', TemplateView.as_view(template_name='home.html'), name='home),')
    path('', include('inventory.urls')),
    re_path(r'api/(?P<version>[v1|v2]+)/', include('api.urls')),
    path('assets/', include('assets.urls')),
    path('dlmr/', include('dlmr.urls', namespace='dlmr')),
    path('reports/', include('reports.urls')),
    path('users/', include('users.urls')),
    path('modes/', include('modes.urls')),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
