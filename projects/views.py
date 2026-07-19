from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from rest_framework.views import APIView
from . import models
from profiles import models as Profilemodels
from . import serializer
import json
from django.http import JsonResponse
from django.forms.models import model_to_dict
from . import functions
from profiles import services
from . import selenium_bot
from selenium.common.exceptions import WebDriverException
import pandas as pd
from datetime import datetime




# Create your views here.
bot = selenium_bot.AutomationBot()
bot.setup_driver()


def ensure_driver():
    global bot

    try:
        bot.driver.current_url
        if bot.wait is None:
            raise AttributeError("WebDriverWait is None")
    except (AttributeError, WebDriverException):
        bot = selenium_bot.AutomationBot()
        bot.driver, bot.wait = bot.setup_driver()
        
def google_maps_bot(request):
    ensure_driver()
    return render(request, "profiles/google_maps.html")
        
def google_maps_automation(request):
    data = json.loads(request.body)
    result = bot.run_automation(**data)
    return JsonResponse ({'status' : result[2], 'time_taken':result[1], 'result': result[0]})
    
def download_excel(request):
    data = json.loads(request.body)
    df = pd.DataFrame(data)
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"results_{datetime.now():%Y%m%d_%H%M%S}.xlsx"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response

class project(APIView):
    def post(self, request):
        try:
            data = request.data
            print("I hvent crosse this line 18")

            profile = Profilemodels.Profiles.objects.get(user_name=data["owner"])
            data["owner"] = profile.id
        
            data["members"] = [profile.user_name] if data["members"] == [] else data["members"]
            members = data["members"]
        
            for i in range(len(members)):
               member = members[i]
               print(member)
               profile_instance = Profilemodels.Profiles.objects.get(user_name=member)
               data["members"][i] = profile_instance.id

            languages = data["languages"]
            for i in range(len(languages)):
                language = languages[i]
                language_instance = models.Language.objects.get_or_create(name=language.lower())[0]
                data["languages"][i] = language_instance.id

            project_serializer = serializer.ProjectSerializer(data=data)

            if project_serializer.is_valid():
                project = project_serializer.save()
                project = serializer.ProjectSerializer(project).data
                project["members"] = services.modify_property(Profilemodels.Profiles, project["members"], "user_name")
                project["languages"] = services.modify_property(models.Language, project["languages"], "name")
                project["owner"] = services.modify_property(Profilemodels.Profiles, project["owner"] ,"user_name")
                print(project)

                return JsonResponse({"status":"success", "message": "Successful", "project": project})

            else:
                print(f"errors: {project_serializer.errors}")
                return JsonResponse({"status":"failed", "message": "Unsuccessful"})

        except Exception as e:
                return JsonResponse({"status":"failed", "message": str(e)})
    def patch(self, request):
        try:
            data = json.loads(request.body)
            profile = Profilemodels.Profiles.objects.get(user_name=data["owner"])
            data["owner"] = profile.id
        
            data["members"] = [profile.user_name] if data["members"] == [] else data["members"]
            members = data["members"]
        
            for i in range(len(members)):
               member = members[i]
               print(member)
               profile_instance = Profilemodels.Profiles.objects.get(user_name=member)
               data["members"][i] = profile_instance.id

            languages = data["languages"]
            for i in range(len(languages)):
                language = languages[i]
                language_instance = models.Language.objects.get_or_create(name=language.lower())[0]
                data["languages"][i] = language_instance.id

            project_instance = models.Project.objects.get(id = data["id"])
            project_serializer = serializer.ProjectSerializer(project_instance, data=data, partial=True)

            if project_serializer.is_valid():
                project = project_serializer.save()
                project = serializer.ProjectSerializer(project).data
                project["members"] = functions.modify_property(Profilemodels.Profiles, project["members"], "user_name")
                project["languages"] = functions.modify_property(models.Language, project["languages"], "name")
                project["owner"] = functions.modify_property(Profilemodels.Profiles, project["owner"] ,"user_name")
                print(project)

                return JsonResponse({"status":"success", "message": "Successful", "project": project})

            else:
                print(f"errors: {project_serializer.errors}")
                return JsonResponse({"status":"failed", "message": "Unsuccessful"})

        except Exception as e:
                return JsonResponse({"status":"failed", "message": str(e)})

    def get(self, request):
        try:
            user_name = request.GET.get("user_name")
            password = request.GET.get("password")
            profile= Profilemodels.Profiles.objects.get(user_name=user_name)

            if profile.password==password:
                projects_serialized = services.serialize_projects(profile)
                
                return JsonResponse({"status":"success", "message": "Successfull", "projects": projects_serialized})
            else:
                return JsonResponse({"status":"failed", "message": "Unauthenticated"})

        except Exception as e:
                return JsonResponse({"status":"failed", "message": str(e)})

    def delete(self, request):
        try:
            user_name = request.GET.get("user_name")
            password = request.GET.get("password")
            project_id = request.GET.get("project_id")
            profile= Profilemodels.Profiles.objects.get(user_name=user_name)

            if profile.password==password:
                project = models.Project.objects.get(id = project_id)
                project.delete()
                return JsonResponse({"status":"success", "message": "Successfull"})
            else:
                return JsonResponse({"status":"failed", "message": "Unauthenticated"})

        except Exception as e:
                return JsonResponse({"status":"failed", "message": str(e)})

    
