import platform
from pathlib import Path

# if platform.system() == 'Darwin':
#     DEBUG = True
# else:
#     DEBUG = False

DEBUG = True

SECRET_KEY = 'i_+=yz8tl1%$noo^s9(lg^h#vusy02z2z-2ip2rsh+h+7v5to_'

SITE_ID = 3

INSTALLED_APPS = [
    # Django Admin
    'admin_interface',
    'colorfield',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # Plugins
    'corsheaders',
    'rest_framework',
    'django_hosts',
    'simple_history',
    'import_export',
    'multiselectfield',
    'mailqueue',
    'constance',
    'constance.backends.database',
    'rangefilter',
    # Applications
    'api',
    'assets',
    'common',
    'dlmr',
    'inventory',
    'modes',
    'reports',
    'users',
    'usergroup'
]

SOCIALACCOUNT_LOGIN_ON_GET=True

AUTHENTICATION_BACKENDS = [
    'usergroup.backends.GroupModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    ]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware'
]

ALLOWED_HOSTS = ['127.0.0.1', '10.1.1.146', '204.52.206.143', 'sadissso.flaglerschools.com', 'dlmrsso.flaglerschools.com']
DEFAULT_HOST = 'www'
CORS_ALLOW_ALL_ORIGINS = True

ROOT_HOSTCONF = 'sadis.hosts'
ROOT_URLCONF = 'sadis.urls'

LOGIN_REDIRECT_URL = 'home'
#LOGOUT_REDIRECT_URL = 'inventory:home'
LOGOUT_REDIRECT_URL = 'login'
REGISTRATION_OPEN = False
ACCOUNT_LOGOUT_ON_GET = True

WSGI_APPLICATION = 'sadis.wsgi.application'

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'constance.context_processors.config',
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages'
        ]
    }
}]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangodb_sadis',
        'USER': 'django',
        'PASSWORD': '<gB24680!',
        'HOST': '10.1.1.145',
        'PORT': '3306'
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_DIRS = [BASE_DIR / 'static_files']
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SIMPLE_HISTORY_FILEFIELD_TO_CHARFIELD = True
SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'form-admin@flaglerschools.com'
EMAIL_HOST_PASSWORD = 'r8pw9aPD2'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

MAILQUEUE_CELERY = False
MAILQUEUE_QUEUE_UP = True
MAILQUEUE_LIMIT = 50
MAILQUEUE_STORAGE = False
MAILQUEUE_ATTACHMENT_DIR = 'mailqueue-attachments'

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'pickle', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'US/Eastern'
CELERY_IGNORE_RESULT = False

from .constance import *
