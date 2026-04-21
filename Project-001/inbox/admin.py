from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Inbox)
admin.site.register(models.Message)
admin.site.register(models.Attachment)