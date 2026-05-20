from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message),
    path('load-inbox/', views.load_inbox),
    path('delete/', views.delete_message),
    path("clear-inbox/", views.clear_inbox),
    path("download/", views.download_file),
    path("block-user/", views.block_user)
    ]
