from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Profile, TermsAndConditions


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("email", "first_name", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ("user",)
    search_fields = ("user",)
    ordering = ("user",)


class TermsAndConditionsAdmin(admin.ModelAdmin):
    model = TermsAndConditions
    list_display = ("user", "accepted", "date_accepted")
    search_fields = ("user", "accepted", "date_accepted")
    ordering = ("user", "date_accepted")


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)