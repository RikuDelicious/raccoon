import datetime
import random

from django.contrib.auth import authenticate
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from articleapp import views
from articleapp.forms import UserCreationForm, ProfileUpdateForm, AccountUpdateForm
from articleapp.models import Post, Tag, User


# Create your tests here.
