from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import FileResponse, Http404
import json, traceback
from . import models
from profiles.models import Profiles, Activity
from django.forms.models import model_to_dict
from . import serializer
from profiles import services
import base64
from django.core.files.base import ContentFile
from django.conf import settings
import os
from django.db.models import Q


# Create your views here.
def block_user(request):
    try:
        profile = request.GET.get("profile")
        blocked_profile = request.GET.get("blocked")

        profile = Profiles.objects.get(user_name = profile)
        blocked_profile = Profiles.objects.get(user_name= blocked_profile)
        if request.GET.get("unblock") == "1":
            try:
                profile.blacklist.remove(blocked_profile)
            except:
                pass
        else:
             profile.blacklist.add(blocked_profile)
        print(profile.blacklist.all())
        return JsonResponse({"status": "successful", "message": "Blocked"})


    except Exception as e:
        return JsonResponse({"status": "failed", "error": str(e)})

def clear_inbox(request):
    try:
        user_name = request.GET.get("user_name")
        password = request.GET.get("password")
        inbox_profile = request.GET.get("inbox_profile")
        profile_instance = Profiles.objects.get(user_name = user_name)
        if password == profile_instance.password:
            inbox = models.Inbox.objects.get(profile = profile_instance)
            messages = inbox.messages.all()
            print(messages)
            for message in messages:
                if (str(message.sender_username) == str(inbox_profile)) or (str(message.receiver_username) == str(inbox_profile)):
                    message.delete()
               
            return JsonResponse({"status": "successful", "message": "Deleted"})
        

        else:
            return JsonResponse({"status":"failed", "message": "Unauthenticated"} )
    except Exception as e:
        return JsonResponse({"status": "failed", "error": str(e)})

def download_file(request):
   file_path = request.GET.get("file_path")
   print(settings.MEDIA_ROOT)
   print(file_path)

   full_path = settings.MEDIA_ROOT+ file_path
   if not os.path.exists(full_path):
        print(full_path)
        raise Http404("File does not exist")

# Return the file response
   return FileResponse(open(full_path, 'rb'), as_attachment=True)

def send_message(request):
    try:
        print("Sending a message")
        data = {**request.FILES, **request.POST}
        for key,value in data.items(): data[key] = value[0]

        profile_instance = Profiles.objects.get(user_name=data["sender_username"])
        receiver_profile = Profiles.objects.get(user_name=data["receiver_username"])
        if (profile_instance in receiver_profile.blacklist.all()) or (receiver_profile in profile_instance.blacklist.all()):
            print("Users blocked")
            return JsonResponse({"status": "failed", "error": "Blocked"})
        activity = Activity.objects.create(profile = receiver_profile, activity= "RM", done_by= profile_instance, detail = "Received message" )
        receiver_profile.active_notifications+=1
        receiver_profile.save()
        print(profile_instance)
        inbox = models.Inbox.objects.get_or_create(profile = profile_instance)[0]
        receiver_inbox = models.Inbox.objects.get_or_create(profile = receiver_profile)[0]
        print(inbox)
        data["sender_username"] = profile_instance
        data["receiver_username"] = receiver_profile
        data_copy = {key: value for key, value in data.items() if key != "file"}
        message = models.Message.objects.create(**data_copy, inbox=inbox)
        message_receiver = models.Message.objects.create(**data_copy, inbox=receiver_inbox)
        print(model_to_dict(message))
        if data.get("file"):
            file = data["file"]
            file_data = file["file_data"]
            print("Hey")
            if "base64," in file_data:
                file_data = file_data.split("base64,")[1]
            file_bytes = base64.b64decode(file_data)
            content_file = ContentFile(file_bytes, name=f"{file['file_name']}")
            print("Hey2")
            instance = models.Attachment.objects.create(**{"file_name": file["file_name"], "file_size": file["file_size"], "path": content_file})
            print("pass")
            instance = instance.save()
            instance.message.set(message, message_receiver)
        message_serialized = serializer.MessageSerializer(message).data
            
        return JsonResponse({"status": "successful", "message": (message_serialized), "attachment": list(message.attachement.all())})

    except Exception as e:
        print("Error2", e, sep=":")
        traceback.print_exc()
        return JsonResponse({"status": "failed", "error": str(e)})


def delete_message(request):
    try:

        data = json.loads(request.body)

        user_name = data["user_name"]
        password = data["password"]
        profile_instance = models.Profiles.objects.get(user_name=user_name)

        if (profile_instance.password == password) and (profile_instance.email_verified):
            message_id = data["id"]
            message = models.Message.objects.get(pk = message_id).delete()
            print(models.Message.objects.filter(pk = message_id))

            return JsonResponse({"status":"successful", "messages": "Successfully deleted"} )

        else:
             return JsonResponse({"status":"failed", "messages": "Profile not authenticated"} )


    except Exception as e:
        return JsonResponse({"status": "failed", "error": e})

def load_inbox(request):
    try:
        user_name = request.GET.get("user_name")
        current_inbox = request.GET.get("current_inbox")
        current_inbox = Profiles.objects.get(user_name=current_inbox)
        profile_instance = Profiles.objects.get(user_name=user_name)
        inbox = models.Inbox.objects.get_or_create(profile = profile_instance)[0]

        messages = models.Message.objects.filter(inbox=inbox)
        messages = [message for message in messages if (message.sender_username == current_inbox or message.receiver_username == current_inbox)]

        returned = models.Message.objects.filter(id__in=[m.id for m in messages if str(m.sender_username) == request.GET.get("current_inbox") ]).update(seen=True)
        
        for i in range(len(messages)):
            message = messages[i]
            time = message.timestamp
            message = model_to_dict(message)
            message["timestamp"] = time
            if message["image"]:
                file = message["image"].read()
                message["image"] = services.bytes_to_base64(file)
            else:
                message["image"] = ""
            message["sender_username"] = Profiles.objects.get(id=message["sender_username"]).user_name
            message["receiver_username"] = Profiles.objects.get(id=message["receiver_username"]).user_name
            message["inbox"] = profile_instance.user_name
            attachements = models.Message.objects.get(id=message["id"]).attachement.all()
            message["file"] = serializer.AttachmentSerializer(attachements,many=True).data
            messages[i] = message
        
        block_status = "None"
        for instance in profile_instance.blacklist.all():
            if instance == current_inbox: 
                block_status = "blocked"
        return JsonResponse({"status":"successful", "messages": messages, "blocked": block_status} )
    except Exception as e:
        print(e)
        return JsonResponse({"status": "failed", "error": str(e)})



