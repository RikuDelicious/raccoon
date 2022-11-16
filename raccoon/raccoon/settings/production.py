import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ["DJANGO_DATABASE_ENGINE"],
        'NAME': os.environ["DJANGO_DATABASE_NAME"],
        'USER': os.environ["DJANGO_DATABASE_USER"],
        'PASSWORD': os.environ["DJANGO_DATABASE_PASSWORD"],
        'HOST': os.environ["DJANGO_DATABASE_HOST"],
        'PORT': os.environ["DJANGO_DATABASE_PORT"],
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# 以下の変数等も本ファイルで設定
# MEDIA_ROOT
# STATIC_ROOT
# LOGGING