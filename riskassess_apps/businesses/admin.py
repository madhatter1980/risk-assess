from django.contrib import admin
from .models import Business, BusinessUser

class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'branch')

class BusinessUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'is_admin', 'invite_accepted', 'id')
    search_fields = ('user__username', 'business__name')
    list_filter = ('is_admin', 'invite_accepted')

admin.site.register(Business, BusinessAdmin)
admin.site.register(BusinessUser, BusinessUserAdmin)