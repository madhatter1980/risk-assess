from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=6, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.branch}"

class BusinessUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    invite_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'business')

    def __str__(self):
        return f"{self.user.username} - {self.business.name} - {self.business.branch}"