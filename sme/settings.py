

from pathlib import Path
from django.contrib.messages import constants
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u7afypyeioy$6!z7+0_n9nhoj^zd4l=1$i5tewe7%v4llfr#9^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [*
    #'89af-177-200-115-250.ngrok-free.app' ,
    #'localhost',
    #'127.0.0.1',
    #'192.168.15.19',
    #'192.168.15.53',    
    # Outros domínios permitidos
    #'177.131.142.27',
    #'kiweln.conteige.cloud',
    #'https://kiweln.conteige.cloud'
]

CSRF_TRUSTED_ORIGINS = ['https://89af-177-200-115-250.ngrok-free.app', 'https://kiweln.conteige.cloud']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # meus apps
    'rh',   
    'admin_acessos',     
    'gestao_escolar',  
    'controle_estoque', 
    'docsGestao_Escolar',  
    'modulo_aluno',
    'ckeditor',
    'ckeditor_uploader' 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sme.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'base_templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #'gestao_escolar.context_processors.verifica_sessoes',
                'gestao_escolar.context_processors.list_turmas',
                'controle_estoque.msg_context_processors.message_user_contexto',                
                'rh.msg_context_processors.message_user_contexto'
                
            ],
        },
    },
]


WSGI_APPLICATION = 'sme.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'base_static',
    BASE_DIR / 'media'
]
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Mudanças do CKEDITOR
# Media_path
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_UPLOAD_PATH = 'uploads/'

# Para responsividade e code snippet
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': None,
        'width' :'100%',
        'extraPlugins': ".".join(
            [
                "codesnippet"
            ]
        )
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Adicione o tipo MIME correto para arquivos JS

import mimetypes
mimetypes.add_type("text/javascript", ".js", True)


# Security settings
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Message settings
MESSAGE_TAGS = {
    constants.DEBUG: 'alert-secondary',
    constants.INFO: 'alert-info',
    constants.SUCCESS: 'alert-success',
    constants.WARNING: 'alert-warning',
    constants.ERROR: 'alert-danger',
}

# DEFINIÇÕES DE SEGURANÇA PARA SESSÕES. 

# 1º define o mecanismo de armazenamento de sessão para 'django.contrib.sessions.backends.cache' ou
# o 'django.contrib.sessions.backends.db' conforme a preferência. Foi escolhido armazenamento em cache
SESSION_ENGINE =   'django.contrib.sessions.backends.cache'

# 2º define a chave de assinatura da sessão
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# 3º Define o tempo de sessão para 1 hora (3600 segundos)
#SESSION_COOKIE_AGE = 3600
LOGIN_URL = 'admin_acessos:login_create'

import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    """
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },"""
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '__main__': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# CONFIRGURAÇAÕ PARA O CONTEIGER.CLOUD
# Porta do servidor HTTP
PORT = int(os.environ.get('PORT', 8000))

# Endereço/Host do servidor HTTP
HOST = os.environ.get('HOST', '0.0.0.0')

"""
Variáveis de Ambiente necessárias:

Nome da Variável: PORT
Valor da Variável: 8000 (ou qualquer outra porta desejada para o servidor HTTP)
HOST:
Nome da Variável: HOST
Valor da Variável: 0.0.0.0 (ou o endereço IP específico que o conteiger.cloud recomenda para o host do servidor HTTP)
"""
