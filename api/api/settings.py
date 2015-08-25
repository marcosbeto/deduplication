"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lf%ybat@gay=0bkma^d1p*^5))pdhav**!%06ti@2(06&f%4g2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'snippets',
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'api.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)


TEMPLATE_DIRS = (
    os.path.dirname( __file__ ) + '/templates'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    # "social_auth.context_processors.social_auth_by_type_backends",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
)


WSGI_APPLICATION = 'api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_engine',
        'NAME': 'deduplication',
        'HOST': 'localhost',
        'PORT': 27017,
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

#CONSTANTS

IMOVELWEB_API_URL_BASE = "http://apim01.imovelweb.com.br"

IMOVELWEB_API_AUTH_URL = IMOVELWEB_API_URL_BASE + "/interface/buscador/dispositivo/registro/"
IMOVELWEB_API_QUERY_URL = IMOVELWEB_API_URL_BASE + "/interface/buscador/buscarmin"
IMOVELWEB_API_QUERY_URL_AD_DETAIL = IMOVELWEB_API_URL_BASE + "/interface/buscador/ver/"
IMOVELWEB_API_QUERY_LOGIN = IMOVELWEB_API_URL_BASE + "/interface/buscador/login"
IMOVELWEB_API_QUERY_SEMILOGIN = IMOVELWEB_API_URL_BASE + "/interface/buscador/semilogin"
IMOVELWEB_API_QUERY_UUID_RETRIEVE = IMOVELWEB_API_URL_BASE + "/interface/buscador/getuuidfromemail/"
IMOVELWEB_API_QUERY_SEND_EMAIL = IMOVELWEB_API_URL_BASE + "/interface/buscador/contactar/email/"

IMOVELWEB_API_QUERY_ADD_FAVORITE = IMOVELWEB_API_URL_BASE + "/interface/buscador/favoritos/agregar/"
IMOVELWEB_API_QUERY_REMOVE_FAVORITE = IMOVELWEB_API_URL_BASE + "/interface/buscador/favoritos/borrar/"
IMOVELWEB_API_QUERY_LIST_FAVORITE = IMOVELWEB_API_URL_BASE + "/interface/buscador/favoritos/listado/"

IMOVELWEB_API_USERNAME = "adonde"
IMOVELWEB_API_PASSWORD = "v1v1radonde"
IMOVELWEB_API_USER_AGENT = "API_RELA"
IMOVELWEB_API_UUID = "4788865e3938759052311306ca032077"
