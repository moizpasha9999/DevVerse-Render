from rest_framework import serializers
from . import models

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Community
        fields="__all__"

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Activity
        fields="__all__"

class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Phone
        fields="__all__"

class ProfileSerializer(serializers.ModelSerializer):
 #   community = serializers.StringRelatedField()
    class Meta:
        model= models.Profiles
        fields="__all__"