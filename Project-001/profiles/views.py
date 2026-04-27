import base64
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.core.exceptions import ObjectDoesNotExist
import smtplib
from email.message import EmailMessage
from . import model_services
from . import services
from rest_framework.views import APIView
from . import models
from . import serializer
from django.forms.models import model_to_dict
from django.views.decorators.csrf import ensure_csrf_cookie
from inbox import models as Inboxmodels
from posts import models as Postmodels
from projects import models as Projectmodels
from projects import serializer as Projectserializer
from projects import functions as Projectfunctions
from django.db.models import Q

# Create your views here.
@ensure_csrf_cookie
def launch_page(request):
    return render(request, "profiles/landing page.html")

@ensure_csrf_cookie
def sign_in(request):
    return render(request, "profiles/Login page.html")

@ensure_csrf_cookie
def sign_up(request):
    return render(request, "profiles/Sign-up page.html")

def home(request):
    return render(request, "profiles/Home.html")

def dashboard(request):
    return render(request, "profiles/Dashboard.html")

def projects(request):
    return render(request, "profiles/Projects.html")

def messages(request):
    return render(request, "profiles/Messages.html")

def activity(request):
    return render(request, "profiles/Activity.html")

def settings(request):
    return render(request, "profiles/Settings.html")

def profile_template(request, user_name):
    try:
        profile = models.Profiles.objects.get(user_name=user_name)
        friends = list(profile.following.all())
        viewer = base64.b64decode(request.GET.get("viewer"))
        viewer = viewer.decode("utf-8")
        print(viewer)
        viewer_profile = models.Profiles.objects.get(user_name=viewer)
            
        for i in range(len(friends)):
               profile_i = friends[i]
               friends[i] = {"id": profile_i.id, "user_name": profile_i.user_name, "profile_picture": profile_i.profile_picture, "jobTitle": profile_i.jobTitle }

        projects_serialized = services.serialize_projects(profile)
        projects_serialized.reverse()
        
        posts = profile.postbox.posts.all() 
        posts_serialized = services.serialize_posts(posts, profile, viewer_profile)
        posts_serialized.reverse()
        profile = model_to_dict(profile)
        profile["phones"] = serializer.PhoneSerializer(models.Phone.objects.filter(profiles=profile["id"]).last()).data
        profile["phones"]["number"] = "+92 "+ str(profile["phones"]["number"])
        return render(request, "profiles/profile_template.html", {"profile":profile , "posts": posts_serialized, "projects_data": projects_serialized, "friends": friends})
    except ObjectDoesNotExist:
        Postmodels.PostBox.objects.get_or_create(profile=profile)
        Inboxmodels.Inbox.objects.get_or_create(profile=profile)
        return profile_template(request, user_name)

def get_usernames(request):
    initials = request.GET.get("initials")
    user = request.GET.get("user_name")
    user = models.Profiles.objects.get(user_name = user)
    print(initials)
    usernames = list(
    models.Profiles.objects
    .filter(user_name__istartswith=initials)
    .exclude(blacklist=user)
    .exclude(user_name=user.user_name)
    .values("user_name", "profile_picture", "jobTitle")
)
    print(usernames)
   
    
    return JsonResponse({"status":"successful", "usernames":usernames})

def follow_profile(request):
    user_name =request.GET.get("user_name")
    password = request.GET.get("password")
    following_profile = request.GET.get("following_profile")
    follow_state = request.GET.get("unfollow")
    user_profile = models.Profiles.objects.get(user_name= user_name)
    profile = models.Profiles.objects.get(user_name = following_profile)
    if user_profile.password == password:
        if follow_state=="0":
            user_profile.following.add(profile)
        else:
            user_profile.following.remove(profile)
        profile.followers = len(list(profile.followed_by.all()))
        profile.save()
        return JsonResponse({"status":"successful", "followers": profile.followers, "message": "Followed successfully"})
    else:
        return JsonResponse({"status":"failed", "message": "Unauthenticated"})


def services_request(request):
    try:
        '''
        objects = models.Profiles.objects.exclude(
        profile_picture__istartswith="data:image/png;base64"
    )
        for profile in objects:
            profile.profile_picture = f"data:image/png;base64,{model_services.image_url_to_base64('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmwCmC6pZjmJZsvvNufFvqxJf7_C73ff3_Bg&s')}"
            profile.save()
            print(profile)
            '''
        from django.apps import apps

        Profile = apps.get_model('profiles', 'Profiles')

        for rel in Profile._meta.related_objects:
                print(rel.name, rel.on_delete)
        return JsonResponse({"status":"Done"})
    except Exception as e:
        print(e)
        return JsonResponse(str(e), safe=False)

class profile(APIView):
    def delete(self, request):
      try:
        data = request.data
        user_name = data["user_name"]
        password = data["password"]
        profile = models.Profiles.objects.get(user_name = user_name)

        if password == profile.password:
            profile.delete()
            return JsonResponse({"status":"successfull"})
      except Exception as e:
            return JsonResponse({"status":"failed", "error":e})

    def get(self, request):
        try:
            profile = request.GET.get("user_name")
            profile = models.Profiles.objects.get(user_name=profile)
            contacts = models.Profiles.objects.filter(
                (
                    Q(sent_messages__receiver_username=profile) |
                    Q(received_messages__sender_username=profile) |
                    Q(followed_by=profile)
                ) &
                ~Q(blacklist=profile)
            ).distinct()
            objects = list(contacts)
            print(objects)
            for i in range(len(objects)):
                profile_i = objects[i]
                Inboxmodels.Inbox.objects.get_or_create(profile=profile)
                unseen = profile.inbox.messages.filter(seen=False, sender_username= profile_i).count()
                objects[i] = {"id": profile_i.id, "user_name": profile_i.user_name, "profile_picture": profile_i.profile_picture, "jobTitle": profile_i.jobTitle, "unseen":unseen }
                print(objects[i])
           
            
            #profiles_objects = serializer.ProfileSerializer(objects, many=True).data
            return JsonResponse({"status":"successfull", "profiles":objects})
        except Exception as e:
            return JsonResponse({"status":"failed", "error":e})

    def patch(self, request):
        profile= request.data
        print(request.method)
        if profile.get("old_user_name"):
            instance = models.Profiles.objects.get(user_name = profile["old_user_name"] )
            profile.pop("old_user_name")

        else:  
             instance = models.Profiles.objects.get(user_name = profile["user_name"] )

        try:
            if profile.get("community"):
                serializer_community = serializer.CommunitySerializer(data={"title":profile["community"]})
            

                if serializer_community.is_valid(): 
                    community= serializer_community.save()
                    profile["community"]= community.id
                    print(profile["community"])
                print(f"errors: {serializer_community.errors}")

            if profile.get("phones"):

                 serializer_phone = serializer.PhoneSerializer(data={"number": profile["phones"], "profiles":instance.id})
                 if serializer_phone.is_valid(): 
                    phone= serializer_phone.save()
                   

                 print(f"errors: {serializer_phone.errors}")
            
  

            serializer_profile= serializer.ProfileSerializer(instance, data=profile, partial=True)
            
            if serializer_profile.is_valid(): 
                profile_final= serializer_profile.save()
            
            else:
                 profile_final="error occured"
            
            print(serializer_profile.errors)
            return JsonResponse({"status":"successful", "profile": {"user_name": profile_final.user_name, "email_id": profile_final.email_id, "email_verified": profile_final.email_verified, "profile_id": profile_final.id}})
          
        except Exception as e:
              return JsonResponse({"status":"failed", "error":str(e)})
    def post(self, request):
        profile= request.data
        try:
            
            if profile.get("community"):
                   serializer_community = serializer.CommunitySerializer(data={})
                   if serializer_community.is_valid(): 
                     community= serializer_community.save()
                     profile["community"]= community.id
                     print(profile["community"])
                   print(f"errors: {serializer_community.errors}")

            
            

            serializer_profile= serializer.ProfileSerializer(data=profile)
            
            if serializer_profile.is_valid(): 
                profile_final= serializer_profile.save()
                profile_finalized = models.Profiles.objects.get(id = profile_final.id)
                inbox = Inboxmodels.Inbox.objects.create(profile=profile_finalized)
                postbox = Postmodels.PostBox.objects.create(profile = profile_finalized)
                print("here")
                if profile.get("phones"):
                    serializer_phone = serializer.PhoneSerializer(data={"profiles":profile_final, "number":profile["phone"]})
                    if serializer_phone.is_valid(): 
                        phone= serializer_phone.save()
                        
                    print(f"errors: {serializer_phone.errors}")
            
            else:
                 profile_final="error occured"
            
            print(serializer_profile.errors)
            print(model_to_dict(profile_final))
            return JsonResponse({"status":"successful", "profile": {"user_name": profile_final.user_name, "email_id": profile_final.email_id, "email_verified": profile_final.email_verified, "profile_id": profile_final.id}})
          
        except Exception as e:
              return JsonResponse({"status":"failed", "error":str(e)})
        
def check_username(request, username):
    try:
        models.Profiles.objects.get(user_name= username)
        return JsonResponse({"status":0})
    except:
        return JsonResponse({"status":1})
def email_verification_page(request):
    return render(request, "profiles/Email Verification page.html/")

def verification_endpoint(request):
    try:
        print(request.body)
        data = json.loads(request.body)
        print(data)
        code = data["code"]
        
        username = data["user_name"]
        instance = models.Profiles.objects.get(user_name=username)
        instance_code = instance.login_status
        if instance_code==code:
            instance.email_verified = True
            instance.save(update_fields=["email_verified"])
            print(model_to_dict(instance))
            return JsonResponse({"status":"successfull", "message":"Redirecting to profile page"})
        else:
            return JsonResponse({"status":"failed", "message":"Incorrect code, try again."})
    except Exception as e:
            return JsonResponse({"status":"failed", "message":str(e)})


def email_authentication(request):
    print(request.body)
    data= json.loads(request.body)
    verified = models.Profiles.objects.get(user_name=data["user_name"]).email_verified
    if not verified:
            email_id = models.Profiles.objects.get(user_name=data["user_name"]).email_id
            login_status= services.get_verification_code()
            email = EmailMessage()
            email["To"]= email_id
            email["From"]="devverseofficial00@gmail.com"
            email["Subject"]="Email Verification code"
            email.set_content(f"Your verification link is {login_status}")
            email.add_alternative(f"""
        <html>
          <body>
            <p style="font-size: 30px; margin-bottom:3px; ">Your verification code is: <a style="font-size: 35px;">{login_status}</a></p>
            <p style="font-size: 30px; ">Please use this code to complete your verification process. This automated email is sent for email verification.</p>
          </body>
        </html>
        """, subtype="html")

            SMTP_HOST="smtp.gmail.com"
            SMTP_PORT=465

            with smtplib.SMTP_SSL( SMTP_HOST, SMTP_PORT) as smtp:
                smtp.set_debuglevel(1)
                smtp.login("devverseofficial00@gmail.com", services.APP_PASSWORD)
                smtp.send_message(email)
    
            profile_object = models.Profiles.objects.update(login_status=login_status)
          
    return JsonResponse({"status":"successful", "verified": verified})
     

def credentials_authentication(request):
    data = json.loads(request.body)
    print(data)
    # data will be in the following format {"user_name":"moizpasha987", "password":"xcybmunmbd89"}
    try:
        print("This line is executed")
        profile_instance = models.Profiles.objects.get(user_name = data["user_name"])
        password =data["password"]
        if profile_instance.password ==  password:
            if data.get("return_data"):

                profile = serializer.ProfileSerializer(profile_instance).data

                if not profile["email_verified"]: return JsonResponse({"status":"failed", "message": "Email not verified"})

                phones = models.Phone.objects.filter(profiles=profile_instance).last()
                print(f"Here I am, {profile_instance.user_name}")
                #phones = None if not(phones.exists()) else phones
                phones = serializer.PhoneSerializer(phones).data
                print(phones)
                community = models.Community.objects.filter(pk=profile["community"]).first()
                community = serializer.CommunitySerializer(community).data

                profile["status"] = "successfull"
                profile["message"]= "Redirecting"
                profile["phones"] = phones
                profile["community"] = community
                
                print(activity)
                return JsonResponse(profile)
            else:
                return JsonResponse({"status":"successful", "message": "Redirecting"})
        else:
            print(profile_instance.password, password, sep="------")
            return JsonResponse({"status":"successful", "message": "Incorrect Password"})
    except Exception as e:
           return JsonResponse({"status":"failed", "message":"Incorrect Password or username", "error":str(e)})

def get_activity(request):
    try:
        user_name = request.GET.get("user_name")
        password = request.GET.get("password")

        profile = models.Profiles.objects.get(user_name=user_name)

        if profile.password == password:
            activities = profile.activities.all()

            activities = serializer.ActivitySerializer(activities, many=True).data
            for activity in activities:
                activity["profile"] = models.Profiles.objects.get(id=activity["profile"]).user_name
                if activity["done_by"]:
                    activity["done_by"] =models.Profiles.objects.get(id=activity["done_by"]).user_name
            profile.active_notifications = 0
            profile.save()

            return JsonResponse({"status":"successful", "message": "Successfull", "activities": list(reversed(activities))})
        else:
            return JsonResponse({"status":"successful", "message": "Incorrect Password"})
    except Exception as e:
           return JsonResponse({"status":"failed",  "error":str(e)})


        