from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
import logging
logging.basicConfig(level=logging.DEBUG)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent 

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Now retrieve secrets strictly from environment (no fallback).
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')        # If missing, this will be None and likely break your app
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
DATABASE_URL = os.getenv('DATABASE_URL')
SITE_ID = int(os.getenv('SITE_ID'))   


#DATABASE_URL = "postgresql://postgres:qsaYzAIPQNssheBNrDfoJIqbGxQQWoTR@junction.proxy.rlwy.net:32147/railway"

LOGOUT_REDIRECT_URL = '/'
# Redirect to the homepage after login
LOGIN_REDIRECT_URL = '/home'

LOGIN_URL = '/accounts/login/'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'devlink.notifications@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = "DevLink <devlink.notifications@gmail.com>"



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'b)2(07%(p#u+0w)xzg2obwkc3%cmbn&7zc--xk@*8&@boms&lf')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'www.campusdev.link',
    'devlink.up.railway.app', 
    'localhost',                                
    '127.0.0.1',                                
    '[::1]',                                    
]

#SECURE_SSL_REDIRECT = True

#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    'https://devlink.up.railway.app',
    'http://127.0.0.1:8000',
    'https://www.campusdev.link',
]
# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',  # Required for allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'projects',
    'cloudinary',
    'cloudinary_storage', #important
]


# Detect if running in production (Railway)
IS_PRODUCTION = os.getenv("RAILWAY_ENVIRONMENT", False)

if IS_PRODUCTION:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
else:
    REDIS_URL = "redis://localhost:6379/1"  # Local Redis server

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.getenv("REDIS_PASSWORD", None) if IS_PRODUCTION else None,
        },
        "TIMEOUT": 600,  
    }
}

SITE_ID = 5  # Hardcoded to ensure it's set correctly

#SITE_ID = 4
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default authentication
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth backend
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ]
    }
}


DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=1800),
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'projects.middleware.RedirectAuthenticatedMiddleware',

    'projects.middleware.ProfileCompletionMiddleware',

]

ROOT_URLCONF = 'DevLink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'projects' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'projects.context_processors.notification_processor',

            ],
        },
    },
]

WSGI_APPLICATION = 'DevLink.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'projects/static/projects'), 
]

# Whitenoise configuration for static and media files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'



DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
    'API_KEY': CLOUDINARY_API_KEY,
    'API_SECRET': CLOUDINARY_API_SECRET,
}

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)


# Media files
MEDIA_URL = '/media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field