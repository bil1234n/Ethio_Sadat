from pathlib import Path
import os
from dotenv import load_dotenv
import mimetypes
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY SETTINGS ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key')

# DEBUG is True locally, but False on Render
DEBUG = True

# Allow Render and Localhost
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '.onrender.com', 
    'www.ethiosadat.com',
    'ethiosadat.com',
    '*']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# CSRF Trust for Render URLs
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    'django.contrib.staticfiles',   
    'cloudinary_storage',           
    
    'cloudinary',    
           
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'api',
    'accounts',
    'products',
    
    'socialMedia',
    'message',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ADD BASE_DIR / 'templates' HERE
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                'products.context_processors.global_categories',
                'accounts.context_processors.notifications_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# --- DATABASE ---
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Use Neon Cloud Database on Vercel
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# --- STATIC FILES (CSS/JS) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure Django development server serves 3D models correctly
mimetypes.add_type("model/gltf-binary", ".glb")
mimetypes.add_type("model/gltf+json", ".gltf")
mimetypes.add_type("model/vnd.usdz+zip", ".usdz")



# 1. Map your .env variables to Cloudinary config
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# 2. Correctly assign Cloudinary for Media and WhiteNoise for Static
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage", # <--- FIXED THIS
    },
}


YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
IG_ACCESS_TOKEN = os.environ.get('IG_ACCESS_TOKEN')
IG_USER_ID = os.environ.get('IG_USER_ID')
FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
GOOGLE_WEB_CLIENT_ID = os.environ.get('GOOGLE_WEB_CLIENT_ID')
GOOGLE_ANDROID_CLIENT_ID = os.environ.get('GOOGLE_ANDROID_CLIENT_ID')

# --- GOOGLE AUTHENTICATION ---
GOOGLE_CLIENT_ID = os.environ.get(
    'GOOGLE_CLIENT_ID', 
    os.environ.get('GOOGLE_CLIENT_ID')
)

# Allow Google One Tap popup to communicate with Django
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
