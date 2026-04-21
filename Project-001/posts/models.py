# Create your models here.
from django.db import models
from profiles.models import Profiles
# Create your models here.

class PostBox(models.Model):
    profile = models.OneToOneField(Profiles, on_delete=models.CASCADE, related_name="postbox")

class Post(models.Model):
    payload = models.TextField()
    postbox = models.ForeignKey(PostBox, on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField(auto_now=True)
    shares = models.IntegerField(default=0)
    pinned = models.BooleanField(default=False)
    image = models.TextField(null=True, blank = True)

    

    
class Like(models.Model):
    profile = models.ForeignKey(Profiles, on_delete=models.SET_NULL, related_name = "liked_post", null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = "post_likes")  
   
    class Meta:
        constraints = [
        models.UniqueConstraint(fields=["profile", "post"], name="unique_like")
    ]

class Comment(models.Model):
    content = models.TextField(blank=False, null=False )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    creater = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name="comments" )
    date_posted = models.DateField(auto_now=True)



class Attachment(models.Model):
    path = models.CharField(max_length=1024, null=False, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="attachement") 


    
