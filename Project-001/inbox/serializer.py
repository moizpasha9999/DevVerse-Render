from rest_framework import serializers
from . import models

class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Inbox
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = "__all__"


class AttachmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Attachment
        fields = "__all__"