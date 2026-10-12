from django.urls import path
from . import views

urlpatterns = [
    # Student Auth & Portal
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('send-request/<int:member_id>/', views.send_request_view, name='send_request'),
    path('requests/', views.requests_list_view, name='requests_list'),
    path('respond-request/<int:request_id>/<str:action>/', views.respond_request_view, name='respond_request'),

    # Instructor / Coordinator Custom Admin Portal
    path('portal-admin/login/', views.admin_login_view, name='custom_admin_login'),
    path('portal-admin/logout/', views.admin_logout_view, name='custom_admin_logout'),
    path('portal-admin/dashboard/', views.admin_dashboard_view, name='custom_admin_dashboard'),
    path('portal-admin/pairs/create/', views.admin_create_pair_view, name='admin_create_pair'),
    path('portal-admin/pairs/<int:pair_id>/delete/', views.admin_delete_pair_view, name='admin_delete_pair'),
]