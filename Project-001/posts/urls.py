from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_post),
    path("get/", views.get_posts),
    path("edit/", views.edit_posts),
    path("like_post/", views.like_post),
    path("post/<int:p_id>", views.render_post)
    ]

