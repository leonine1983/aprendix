from pathlib import Path
from django.contrib.messages import constants
import os
from decouple import config, Csv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG',  cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='*')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())

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
    #'controle_estoque', 
    'docsGestao_Escolar',  
    'modulo_aluno',
    'modulo_professor',
    # 🔹 Base institucional
    'core.apps.CoreConfig',

    # 🔹 Domínio Merenda
    "merendaEscolar",

    # 🔹 Módulos dependentes
    "modulo_Merendeiras",
    "modulo_coordenacao",

    
    'ckeditor',
    'ckeditor_uploader',    
    'widget_tweaks',
    'django.contrib.humanize',
    "django_extensions",
    "arquitetura"

]

MIDDLEWARE = [    
    'django.middleware.security.SecurityMiddleware',    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'sme.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'base_templates',
            BASE_DIR / 'templates',
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
                #'controle_estoque.msg_context_processors.message_user_contexto',                
                'rh.msg_context_processors.message_user_contexto'
                
            ],
        },
    },
]


WSGI_APPLICATION = 'sme.wsgi.application'

# DATABASE ------------------------------------------------------
# DATABASE ------------------------------------------------------
DB_SQLITE = config('DB_SQLITE', default=False, cast=bool)

if DB_SQLITE:
    # Banco SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

else:
    # Banco PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
# END DATABASE ----------------------------------------------------

# END DATABASE ----------------------------------------------------



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

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
#SESSION_ENGINE = 'django.contrib.sessions.backends.db'


import mimetypes
#mimetypes.add_type("text/javascript", ".js", True)
import mimetypes
mimetypes.types_map[".js"] = "text/javascript"


# Security settings
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True



"""
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL') """

# Configurações de e-mail 
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='cauans.technology@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



# Message settings
MESSAGE_TAGS = {
    constants.DEBUG: 'alert-secondary',
    constants.INFO: 'alert-info',
    constants.SUCCESS: 'alert-success',
    constants.WARNING: 'alert-warning',
    constants.ERROR: 'alert-danger',
}



# ===============================
# CONFIGURAÇÕES DE SESSÃO E COOKIES
# ===============================

# Armazena sessões no banco de dados (persistente e seguro em produção)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Tempo de expiração da sessão (1 hora)
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cookies de sessão e CSRF seguros (ative se estiver em HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Evita acesso do JavaScript ao cookie da sessão
SESSION_COOKIE_HTTPONLY = True

# Restringe envio de cookies para o mesmo site
SESSION_COOKIE_SAMESITE = "Strict"

# URL de login
LOGIN_URL = 'admin_acessos:login_create'

# 3º Define o tempo de sessão para 1 hora (3600 segundos)
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = False



