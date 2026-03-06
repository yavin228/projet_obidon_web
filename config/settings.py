from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-obidon'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'core',  # ton app principale
    'django.contrib.humanize',  # AJOUTÉ pour les filtres de template de formatage de nombres
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.views.currency_context',  # CORRIGÉ: pointe vers la fonction dans views.py
                'core.context_processors.global_filters'
            ],
            'builtins': [  # AJOUTÉ pour charger automatiquement les tags de template
                'core.templatetags.currency_tags',  # Charge automatiquement tes tags de devise
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentification Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth Settings
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_REDIRECT_URL = '/account/'
LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_AUTO_SIGNUP = True

# EMAIL CONFIG
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Pour développement
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Pour la production
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'yavinmitekor@gmail.com'
EMAIL_HOST_PASSWORD = ''  # À configurer en production
DEFAULT_FROM_EMAIL = 'Obidon <noreply@obidon.com>'

# Configuration des devises - AMÉLIORÉE
CURRENCY_SETTINGS = {
    'DEFAULT_CURRENCY': 'XOF',
    'SUPPORTED_CURRENCIES': ['XOF', 'USD', 'EUR'],
    'CACHE_TIMEOUT': 3600,  # 1 heure
    'EXCHANGE_RATES': {  # Taux par défaut
        'XOF': {'USD': 0.001667, 'EUR': 0.001525},
        'USD': {'XOF': 600.0, 'EUR': 0.92},
        'EUR': {'XOF': 655.957, 'USD': 1.08}
    },
    'SYMBOLS': {
        'XOF': 'FCFA',
        'USD': '$',
        'EUR': '€'
    }
}

# Session configuration - IMPORTANT pour stocker la devise
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Utilise la base de données
SESSION_COOKIE_AGE = 1209600  # 2 semaines en secondes
SESSION_SAVE_EVERY_REQUEST = True  # Met à jour la session à chaque requête
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Garde la session ouverte

# Internationalization pour les devises
USE_L10N = False  # Désactivé pour contrôler manuellement le format des devises
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ' '
NUMBER_GROUPING = 3
DECIMAL_SEPARATOR = ','

# Logging pour déboguer
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Plus détaillé pour déboguer
            'propagate': False,
        },
    },
}


# ========== CONFIGURATION TAUX DE CHANGE EN TEMPS RÉEL ==========
EXCHANGE_RATE_API_KEY = '3c4ef4cefde07113188c5702'  # VOTRE CLÉ API
USE_REALTIME_EXCHANGE_RATES = True  # Activer les taux en temps réel
EXCHANGE_RATE_CACHE_TIMEOUT = 3600  # Cache de 1 heure

# ✅ CACHE EN MÉMOIRE (pas de Redis requis - fonctionne immédiatement)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'obidon-currency-cache',
    }
}