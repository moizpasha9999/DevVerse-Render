from django.urls import path
from . import views


urlpatterns = [
   path("project/", views.project.as_view()),
   path("google_maps_page/", views.google_maps_bot),
   path("google_maps_bot/", views.google_maps_automation),
   
    
]