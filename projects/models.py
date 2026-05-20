from django.db import models
from profiles import models as Profilemodels

# Create your models here.
class Language(models.Model):
    name = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.TextField(null=False, blank=False)
    description = models.TextField (null=False, blank=False)
    date_created = models.DateField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(Profilemodels.Profiles, on_delete = models.CASCADE, related_name="owned_projects")
    github_username = models.CharField(max_length=256, default="")
    members = models.ManyToManyField(Profilemodels.Profiles, related_name='member_of_projects')
    languages = models.ManyToManyField(Language, related_name='projects')




    



    