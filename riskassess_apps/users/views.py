from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import login
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ProfileUpdateForm,
    InviteSignupForm,
)

from .models import User, Profile, TermsAndConditions

from riskassess_apps.businesses.models import BusinessUser


def signup(request):
    if request.method == "POST":
        # Process the form data
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user to the database
            user = form.save()
            
            # Save the terms and conditions acceptance
            TermsAndConditions.objects.create(
                user=user,
                accepted=form.cleaned_data['accepted_terms'],
                user_first_name=user.first_name,
                user_last_name=user.last_name,
                user_email=user.email
            )

            # Log in the user
            login(request, user)

            messages.success(
                request,
                f"Welcome {user.first_name} at {user.email}.",
            )

            # Redirect to a add business details page
            return redirect("add_business")
    else:
        # Display the signup form
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("user_profile")


@login_required
def invite_signup(request):
    if request.method == "POST":
        form = InviteSignupForm(request.POST)
        business_user = BusinessUser.objects.filter(user=request.user).first()
        business = business_user.business if business_user else None
        if form.is_valid():
            user = form.save(commit=False)
            user.set_unusable_password()  # Set unusable password to prevent login without setting password
            user.save()

            # Generate token for setting password
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Email subject
            subject = "Set your password"

            # Plain text message
            text_message = render_to_string(
                "registration/set_password_email.txt",
                {
                    "user": user,
                    "domain": request.get_host(),
                    "uid": uid,
                    "token": token,
                    "sent_by": request.user,
                },
            )

            # HTML message
            html_message = render_to_string(
                "registration/set_password_email.html",
                {
                    "user": user,
                    "domain": request.get_host(),
                    "uid": uid,
                    "token": token,
                    "sent_by": request.user,
                },
            )

            # Create the email
            email = EmailMultiAlternatives(
                subject, text_message, settings.DEFAULT_FROM_EMAIL, [user.email]
            )
            email.attach_alternative(html_message, "text/html")

            # Send the email
            email.send()

            # If the user is an admin,    them as an admin for the business and create a BusinessUser object
            if form.cleaned_data["is_admin"]:
                BusinessUser.objects.create(user=user, business=business, is_admin=True)
            else:
                # Assign the user to the same business model as the user who invited them
                BusinessUser.objects.create(user=user, business=business)
            # message to show user that email has been sent
            messages.success(
                request,
                f"An email has been sent to {user.email} with a link to set their password.",
            )
            return redirect("business_users")
    else:
        form = InviteSignupForm()
    return render(request, "registration/invite_signup.html", {"form": form})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def resend_link(request, user_id):
    user = get_object_or_404(User, id=user_id)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Email subject
    subject = "Set your password"

    # Plain text message
    text_message = render_to_string(
        "registration/set_password_email.txt",
        {
            "user": user,
            "domain": request.get_host(),
            "uid": uid,
            "token": token,
            "sent_by": request.user,
        },
    )

    # HTML message
    html_message = render_to_string(
        "registration/set_password_email.html",
        {
            "user": user,
            "domain": request.get_host(),
            "uid": uid,
            "token": token,
            "sent_by": request.user,
        },
    )

    # Create the email
    email = EmailMultiAlternatives(
        subject, text_message, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
    email.attach_alternative(html_message, "text/html")

    # Send the email
    email.send()

    return Response({'success': True}, status=status.HTTP_200_OK)


def invite_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                # Update invite_accepted field
                business_user = get_object_or_404(BusinessUser, user=user)
                business_user.invite_accepted = True
                business_user.save()
                login(request, user)
                messages.success(
                    request, "Your password has been set. Welcome to the site!"
                )
                return redirect("user_profile")
        else:
            form = SetPasswordForm(user)
        business_user = BusinessUser.objects.filter(user=user).first()
        business = business_user.business if business_user else None
        context = {"form": form, "business": business}
        return render(
            request, "registration/invite_password_reset_confirm.html", context
        )
    else:
        messages.error(request, "The password reset link is invalid.")
        return redirect("password_reset")


@login_required
def user_profile(request):
    user = request.user

    # Fetch the user's profile
    profile = get_object_or_404(Profile, user=user)

    # Fetch business user and related data if exists
    business_user = BusinessUser.objects.filter(user=user).select_related('business').first()

    # Extract business and member count if a business user exists
    business = business_user.business if business_user else None
    members = (
        BusinessUser.objects.filter(business=business).count() if business else 0
    )

    context = {
        "profile": profile,
        "business_user": business_user,
        "business": business,
        "members": members,
    }

    return render(request, "registration/user_profile.html", context)


@login_required
def update_user_profile(request):
    if request.method == "POST":
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profile")
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(
        request,
        "registration/update_profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )