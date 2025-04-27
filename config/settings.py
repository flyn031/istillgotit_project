# config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv
import sys # Needed for checking runserver

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file in the project root
load_dotenv(BASE_DIR / '.env')

# --- Security Settings ---
# Make sure SECRET_KEY is set in your .env file
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # Provide a default for initial setup/migrations if .env is missing, but warn
    print("WARNING: SECRET_KEY not found in .env file. Using insecure default.")
    SECRET_KEY = 'django-insecure-fallback-key-replace-this-in-env!' # CHANGE THIS IN .env

# DEBUG is True only if explicitly set to 'True' in .env, otherwise False
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Define ALLOWED_HOSTS based on .env or default to localhost for DEBUG
# Example .env: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
allowed_hosts_str = os.getenv('ALLOWED_HOSTS')
if allowed_hosts_str:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',')]
elif DEBUG:
    # Default allowed hosts for development using runserver
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    # ALLOWED_HOSTS must be set in .env for production (when DEBUG=False)
    ALLOWED_HOSTS = []
    # Optional: Raise an error if ALLOWED_HOSTS is empty in production,
    # but allow management commands like collectstatic to run.
    # Check if it's a command that requires hosts (like runserver) vs one that doesn't
    # This is a simplification; more robust checks might be needed for edge cases.
    is_server_command = any(cmd in sys.argv for cmd in ['runserver', 'daphne', 'gunicorn', 'uvicorn'])
    if is_server_command and not ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be set in the .env file when DEBUG is False.")


# --- Application definition ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',          # Core authentication framework
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',   # Manages static files

    # Local apps
    'users.apps.UsersConfig',       # Your users app (now contains CustomUser)
    'players.apps.PlayersConfig',   # Your players app

    # Third-party apps
    'crispy_forms',                 # For better form rendering
    'crispy_bootstrap5',            # Bootstrap 5 template pack for crispy-forms
    # 'widget_tweaks',              # Removed as crispy-forms is preferred and used
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add WhiteNoiseMiddleware here if using it for static files in production (after SecurityMiddleware)
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Manages sessions across requests
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',        # Protects against Cross Site Request Forgery
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Associates users with requests using sessions
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls' # Points to your main urls.py file (config/urls.py)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Add project-level templates directory
        'DIRS': [BASE_DIR / 'templates'],
        # Allows Django to find templates inside app subdirectories (e.g., players/templates/)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # Adds the 'request' object to template context
                'django.contrib.auth.context_processors.auth',   # Adds 'user' and 'perms' objects to template context
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# --- Database ---
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# Ensure DB details are correctly set in your .env file
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost') # Default to localhost if not set
DB_PORT = os.getenv('DB_PORT', '5432')      # Default to 5432 if not set

# Check if essential DB settings are present for PostgreSQL
if not all([DB_NAME, DB_USER, DB_PASSWORD]):
     print("WARNING: Database credentials (DB_NAME, DB_USER, DB_PASSWORD) missing or incomplete in .env file.")
     # Fallback or raise error - For now, let Django raise ImproperlyConfigured if engine requires them
     DATABASES = {}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }


# --- Password validation ---
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# --- Internationalization ---
# https://docs.djangoproject.com/en/stable/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static files (CSS, JavaScript, Images served by your web server) ---
# https://docs.djangoproject.com/en/stable/howto/static-files/
STATIC_URL = '/static/'

# Directory where `collectstatic` will gather files for deployment.
# Needs to be an absolute path. Should be outside your main app directories.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Optional: Directories where Django looks for additional static files (besides app static/ dirs)
# STATICFILES_DIRS = [BASE_DIR / 'static'] # Uncomment if you have a project-level static dir


# --- Media files (User-uploaded content) ---
# https://docs.djangoproject.com/en/stable/ref/settings/#media-root
MEDIA_URL = '/media/' # URL prefix for media files served from MEDIA_ROOT
MEDIA_ROOT = BASE_DIR / 'media' # Absolute filesystem path to the directory for user uploads


# --- Default primary key field type ---
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Custom User Model ---
AUTH_USER_MODEL = 'users.CustomUser' # Tells Django to use your custom user model defined in the 'users' app


# --- Authentication URLs ---
# IMPORTANT: These URL names ('login', 'home') must match the 'name' kwarg
# in your path() definitions in config/urls.py or included URLconfs.
# Make sure these names exist at the project level or within an included app namespace.
# If using django.contrib.auth.urls, 'login' is provided. 'home' needs to be defined by you.

# Where to redirect users if they access @login_required views without being logged in
LOGIN_URL = 'login'

# Where to redirect users after successful login if no 'next' parameter is provided
LOGIN_REDIRECT_URL = 'players:profile_detail' # Redirects to the URL named 'profile_detail' within the 'players' app namespace

# Where to redirect users after successful logout
LOGOUT_REDIRECT_URL = 'home'


# --- Crispy Forms Settings ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# --- Optional: Email Configuration (Example using console backend for development) ---
# For development, print emails to the console:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, configure SMTP settings using environment variables:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587)) # 587 is common for TLS
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
# EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true' # Use if port is 465
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER') # Your email address
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') # Your email password or app password
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER) # Email shown in 'From' field