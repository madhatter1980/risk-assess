from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=False)
    last_name = models.CharField(_("last name"), max_length=30, blank=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Remove default 'username' and other fields here

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.email
    

class TermsAndConditions(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    date_accepted = models.DateTimeField(auto_now_add=True)
    user_first_name = models.CharField(max_length=30, blank=True)
    user_last_name = models.CharField(max_length=30, blank=True)
    user_email = models.EmailField(blank=True)

    def __str__(self):
        return self.user_email
