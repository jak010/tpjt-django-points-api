from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xsyb&flc!%uq7n=$#)wdx24=6hzu=l)i#+q*=zqyo@cyv_b)h-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'points_db',
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': '127.0.0.1',
        'PORT': '23306',
        'OPTIONS': {
            'charset': 'utf8mb4'
        },
        "CONN_MAX_AGE": 600
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# INSTALLED_APPS
DEVELOP_APPS = [
    'django_extensions',
    'src.apps',

]

INSTALLED_APPS = INSTALLED_APPS + DEVELOP_APPS

# SQL LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sql': {
            '()': 'django_sqlformatter.SqlFormatter',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'sql',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django로 구현하는 실시간 적립금 조회 서비스',  # OpenAPI 3.0 페이지 타이틀,
    'DESCRIPTION': '',  # OpenAPI 3.0 페이지 설명,
    'VERSION': '1.0.0',  # 버전 정보
    'SERVE_INCLUDE_SCHEMA': False,
    'SORT_OPERATION_PARAMETERS': False,  # 이걸 추가하면 parameter를 class에 정의한 필드 순서대로 Swagger에 노출 시킬 수 있음
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
