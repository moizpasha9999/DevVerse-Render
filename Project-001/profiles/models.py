from django.db import models
from profiles import model_services as services
from django.conf import settings
import os, base64
import base64
from django.core.files import File

# Create your models here.
class Community(models.Model):
    communities = [
    ("Python", "Python Community"),
    ("JavaScript", "JavaScript Community"),
    ("Java", "Java Community"),
    ("C++", "C++ Community"),
    ("C#", "C# Community"),
    ("Go", "Go Community"),
    ("Rust", "Rust Community"),
    ("Ruby", "Ruby Community"),
    ("PHP", "PHP Community"),
    ("Swift", "Swift Community"),
    ("Kotlin", "Kotlin Community"),
    ("TypeScript", "TypeScript Community"),
    ("R", "R Community"),
    ("C", "C Community")
]
    title=models.CharField(max_length=255, choices=communities, default="Python")
    def __str__(self):
         return self.title

class Profiles(models.Model):
    first_name=models.CharField(max_length=255, null=False, blank=False)
    last_name=models.CharField(max_length=255, null=False, blank=False)
    user_name=models.CharField(max_length=255, null=False, blank=False, unique=True)
    date_of_birth=models.DateField(null=True, blank=True)
    community=models.ForeignKey(Community, on_delete=models.SET_NULL, related_name="profiles", blank=True, null=True)
    about_info=models.TextField(default="")
    date_created=models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=255, null=False, blank=False)
    email_id = models.EmailField(null=True, blank=False, default="unknown@gmail.com")
    following = models.ManyToManyField("self", symmetrical=False, blank=True,  related_name="followed_by")
    blacklist = models.ManyToManyField("self", symmetrical=False, blank=True,  related_name="blocked_by")
    followers = models.PositiveBigIntegerField(default=0)
    projects = models.PositiveIntegerField(default=0)
    email_verified = models.BooleanField(default=False)
    login_status = models.CharField(max_length=255, default="")
    location = models.CharField(max_length=255, default="")
    profile_picture = models.ImageField(null=True, blank = True, upload_to="profile_pictures/", default='profile_pictures/blank_profile.png')
    jobTitle = models.TextField(null=True, blank=True)
    active_notifications =models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user_name

    def save(self, *args, **kwargs):
        self.password = services.encrypted(self.password)
       
        
        super().save(*args, **kwargs)

class Phone(models.Model):
    number = models.PositiveBigIntegerField(default=0)
    profiles = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name="phones")

class Activity (models.Model):
    activities = [
        ("Received message", "RM"),
        ("Follwed You", "FU"),
        ("Logged in", "LI"),
        ]
    activity = models.CharField(max_length=255, choices=activities, null=False, blank=False)
    profile = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name="activities")
    done_by = models.ForeignKey(Profiles, on_delete=models.CASCADE, null=True, blank=True, related_name="performed_activities")
    detail = models.TextField(blank=False, null=False)
    time = models.DateTimeField(auto_now_add=True)
