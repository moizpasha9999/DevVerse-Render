from django.urls import path
from . import views


urlpatterns = [
    path('', views.launch_page),
    path('sign-in/', views.sign_in, name='login_page'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('profile/', views.profile.as_view()),
    path('reset-password/', views.reset_password),
    path('email_authentication/', views.email_authentication),
    path('authentication/', views.credentials_authentication),
    path("Email-Verification/", views.email_verification_page),
    path("check_username/<str:username>/", views.check_username),
    path("services/", views.services_request),
    path("email-verification-link/", views.verification_endpoint),
    path("redirect_profile/", views.credentials_authentication),
    path("get-usernames/", views.get_usernames),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/', views.projects, name='projects'),
    path('messages/', views.messages, name='messages'),
    path('activity/', views.activity, name='activity'),
    path('settings/', views.settings, name='settings'),
    path("get_activity/", views.get_activity),
    path("user/profile/<str:user_name>/", views.profile_template),
    path("follow/profile/", views.follow_profile)
    
]