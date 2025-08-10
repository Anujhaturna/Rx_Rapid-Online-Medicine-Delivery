from pathlib import Path
import os
from django.urls import reverse_lazy

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = 'django-insecure-34m*jv&cxo-&%+7(0#at+++q&_1=i4-^!jo73o0v^b+m^k0lvh'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your custom apps
    'Customer',
    'medical',
    'Manager',
    'Medadmin',

    # Third-party apps
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'RxRapid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RxRapid.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom user model
AUTH_USER_MODEL = 'Customer.CustomerUser'  # Change if using default User

# Authentication redirects
LOGIN_URL = reverse_lazy('customer_login')
LOGIN_REDIRECT_URL = reverse_lazy('customer_dashboard')

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'Customer/static',
    BASE_DIR / 'medical/static',
    BASE_DIR / 'Manager/static',
    BASE_DIR / 'Medadmin/static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mcainternaman@gmail.com'
EMAIL_HOST_PASSWORD = 'kybh sqfj lirk qybh'
DEFAULT_FROM_EMAIL = 'RxRapid <mcainternaman@gmail.com>'

# Razorpay (dummy)
RAZORPAY_KEY_ID = 'your-razorpay-key-id'
RAZORPAY_KEY_SECRET = 'your-razorpay-key-secret'

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login settings (for manager)
LOGIN_URL = 'manager_login'
LOGIN_REDIRECT_URL = reverse_lazy('manager_dashboard')

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

RAZORPAY_KEY_ID = "rzp_live_gUGMzzVnhT5cDP"
RAZORPAY_KEY_SECRET = "MArClNraQJo8ynAdPus0M2Ov"
