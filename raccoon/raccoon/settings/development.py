from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-m=$(!zp$+6&o#4@bqbi@gac@p2f=rx$*9r#t@wx_3!dmk6ie4+"

# django-tailwind の設定
TAILWIND_APP_NAME = "theme"

INSTALLED_APPS += ["tailwind", "theme", "django_browser_reload"]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

# 以下の変数等も本ファイルで設定
# MEDIA_ROOT
# STATIC_ROOT
# LOGGING
