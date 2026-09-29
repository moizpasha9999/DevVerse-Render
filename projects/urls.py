from django.urls import path
from . import views


urlpatterns = [
   path("project/", views.project.as_view()),
   path("upload/", views.drive_upload_page, name="drive_upload_page"),
   path("upload-file/", views.drive_upload, name="drive_upload"),
   
    
]