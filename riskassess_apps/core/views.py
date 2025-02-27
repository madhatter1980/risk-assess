from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings

from .forms import ContactForm

from riskassess_apps.businesses.models import Business, BusinessUser


def home(request):
    return render(request, "core/home.html")


def resource_timeout(request):
    return render(request, "core/resource_timeout.html")


def resource_hazard(request):
    return render(request, "core/resource_hazard.html")


def resource_hierarchy(request):
    return render(request, "core/resource_hierarchy.html")


def resource_control(request):
    return render(request, "core/resource_control.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            subject = form.cleaned_data.get("subject")
            message = form.cleaned_data.get("message")
            
            full_message = f"""
            Received message from: {email}
            
            Subject: {subject}
            
            ________________________

            {message}

            ________________________
            """
            send_mail(
                subject="Contact Form Submission",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL_CONTACT_FORM],
            )
            return redirect("contact_success")
    else:
        form = ContactForm()
    
    return render(request, "core/contact.html", {"form": form})


def contact_success(request):
    return render(request, "core/contact_success.html")