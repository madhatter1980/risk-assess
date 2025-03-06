from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from .models import User, Profile


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    accepted_terms = forms.BooleanField(required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "accepted_terms", "captcha")


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ( "info",)


class InviteSignupForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": ("First Name"),
            }
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": ("Last Name"),
            }
        ),
    )
    is_admin = forms.BooleanField(
        label="Is Admin",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "is_admin")
