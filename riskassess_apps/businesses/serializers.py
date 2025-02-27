from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import BusinessUser

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class BusinessUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = BusinessUser
        fields = '__all__'