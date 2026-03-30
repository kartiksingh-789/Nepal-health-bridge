from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-ijxk&abfc0@82p5ejf0&lw$s)2jvez2d4%+^sa84)5cc@=*23q"

# Check if running on PythonAnywhere
ON_PA = os.environ.get('PYTHONANYWHERE_DOMAIN') is not None

# FOR LOCAL: DEBUG = True, FOR PA: DEBUG = False
DEBUG = not ON_PA

ALLOWED_HOSTS = ['*'] if DEBUG else [os.environ.get('PYTHONANYWHERE_DOMAIN'), 'localhost', '127.0.0.1']

# Set Site URL dynamically for callback payments (eSewa/Khalti)
if ON_PA:
    SITE_URL = "https://kartiksingh789.pythonanywhere.com"
else:
    SITE_URL = "http://localhost:8000"


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "directory",      # HealthBridge app
    "pharmacy",       # e-Pharmacy app
]

# ── Custom User Model (pharmacy uses its own User) ──────────────────
AUTH_USER_MODEL = 'pharmacy.User'

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "nepal_health_bridge.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pharmacy.context_processors.session_user",  # ← pharmacy context
            ],
        },
    },
]

WSGI_APPLICATION = "nepal_health_bridge.wsgi.application"

# ── Database ─────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── Password Validation ──────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Internationalisation ─────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE      = "UTC"
USE_I18N       = True
USE_TZ         = True

# ── Static & Media Files ─────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL   = "/media/"                  # ← NEW
MEDIA_ROOT  = BASE_DIR / "media"         # ← NEW

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# ── Site URL (used by eSewa/Khalti callbacks) ────────────────────────
SITE_URL = 'http://localhost:8000'       # ← NEW

# ── eSewa ────────────────────────────────────────────────────────────
ESEWA_PRODUCT_CODE = 'EPAYTEST'
ESEWA_SECRET_KEY   = '8gBm/:&EnhH.1/q'
ESEWA_VERIFY_URL   = 'https://rc.esewa.com.np/api/epay/transaction/status/'

# ── Khalti ───────────────────────────────────────────────────────────
KHALTI_SECRET_KEY   = 'test_secret_key_f59e8b7d18b4499ca40f68195a846e9b'
KHALTI_INITIATE_URL = 'https://a.khalti.com/api/v2/epayment/initiate/'
KHALTI_VERIFY_URL   = 'https://a.khalti.com/api/v2/epayment/lookup/'