from django.db import models
from profiles.models import Profiles
# Create your models here.

def upload_file_path(instance, filename):

    # Use your logic: for example, sender_id & receiver_id
    sender_id = instance.message.sender_username.id
    receiver_id = instance.message.receiver_username.id

    return f"inbox/user_data/user_{sender_id}_to_{receiver_id}/{filename}"

class Inbox(models.Model):
    profile = models.OneToOneField(Profiles, on_delete=models.CASCADE, related_name="inbox")

class Message(models.Model):
    sender_username = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name="sent_messages")
    receiver_username = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name="received_messages")
    payload = models.TextField()
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE, related_name="messages")
    timestamp = models.TimeField(auto_now=True)
    image = models.TextField(null=True, blank=True);
    seen = models.BooleanField(default= False)
    

class Attachment(models.Model):
    path = models.FileField(upload_to=upload_file_path)
    file_name = models.CharField(max_length=1024, null=False, blank=False)
    file_size = models.DecimalField(decimal_places=2, default = 0.00, max_digits=5)
    message = models.ManyToManyField(Message, related_name="attachement", blank=True) 



    
