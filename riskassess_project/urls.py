from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("riskassess_apps.users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("riskassess_apps.core.urls")),
    path("business/", include("riskassess_apps.businesses.urls")),
    path("timeouts/", include("riskassess_apps.timeouts.urls")),
]