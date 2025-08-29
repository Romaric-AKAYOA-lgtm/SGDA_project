from pathlib import Path
import os
from django.urls import reverse_lazy
from dotenv import load_dotenv

# settings.py



# Redirige automatiquement les utilisateurs non connectés vers /login/
LOGIN_URL = reverse_lazy('compte:login')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0&1jdxl9m+2^9s#e5gq03vv*z1+^%^cru(o6haejoe__t8stun'

# SECURITY WARNING: don't run with debug turned on in production!
# Mode debug pour le développement
DEBUG = True
# Ne transmettre les cookies de session que via HTTPS
SESSION_COOKIE_SECURE = False  

# Pour sécuriser aussi le cookie CSRF
CSRF_COOKIE_SECURE = False 
ALLOWED_HOSTS = []
#ALLOWED_HOSTS = []
ALLOWED_HOSTS = [
    '127.0.1.12',   # pour le serveur local
    'localhost',    # pour le développement local
    'romaric.com',  # domaine principal
    'www.romaric.com'  # sous-domaine
]
AUTH_USER_MODEL = 'personne.Personne'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Activation',

    #module de connexion des utilisateurs
    'compte',
    # Apps Référentiel
    'referentiel',
    'referentiel.structure',
    'referentiel.fonction',
    'referentiel.unite',
    'referentiel.organisation_unite',
    'referentiel.personne',
    # Apps Gestion Personnel
    'Gestion_personnel',
    'Gestion_personnel.employe',
    'Gestion_personnel.operation',
    'Gestion_personnel.absence',

    'Gestion_adherent',
    'Gestion_adherent.Inscription_adherent',
    'Gestion_adherent.Inscription_adherent.tuteur',
    'Gestion_adherent.Inscription_adherent.adherent',
    'Gestion_adherent.Inscription_adherent.suiviTuteurAdherent',
    'Gestion_adherent.Prise_en_charge_adherent',
    'Gestion_adherent.Cotisation_adherent',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Une seule fois, doit être avant AuthenticationMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Toujours après SessionMiddleware
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # DOIT venir après SessionMiddleware
    'compte.middleware.LoginRequiredMiddleware',  # Middleware perso pour exiger login

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'Activation.activation_middleware.ActivationMiddleware',  # à activer si nécessaire
]

ROOT_URLCONF = 'SGDA_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],  # ton dossier templates principal
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # obligatoire si tu utilises request dans tes templates
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'compte.context_processors.administration',  # Middleware perso pour exiger login
                 'Activation.context_processors.check_activation',  # Vérifiez ce chemin
               'referentiel.structure.context_processors.administration',  # ajoute ce context processor personnalisé ici
            ],
        },
    },
]

WSGI_APPLICATION = 'SGDA_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

''' 
# Base de données SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

'''
load_dotenv()  # charge les variables depuis .env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# Internationalisation
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Brazzaville'
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Fichiers média
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Champ ID par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BASE_DIR = Path(__file__).resolve().parent.parent  # si ce n’est pas déjà défini


# Assure que le dossier logs existe
logs_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'detailed': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
    },

    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(logs_dir, 'transactions.log'),
            'formatter': 'detailed',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'transactions': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# cofniguration de talwin 
TAILWIND_APP_NAME = 'theme'
if DEBUG:
    # Add django_browser_reload only in DEBUG mode
    INSTALLED_APPS += ['django_browser_reload']
if DEBUG:
    # Add django_browser_reload middleware only in DEBUG mode
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]