from django.forms.models import model_to_dict
from . import models
from projects import models as projectModels
from posts import serializer as postSerializer
from posts import models as postModels
from projects import serializer as projectsSerializer
import random


APP_PASSWORD="zkjx wagf vzid xinp"
def get_verification_code():
    code = random.randint(100000, 999999)
    return code

def modify_property(model,unmodified_list, property):
    if type(unmodified_list) is list:
        for i in range(len(unmodified_list)):
            element_id = unmodified_list[i]
            element = model_to_dict(model.objects.get(id = element_id ))
            unmodified_list[i] = element[property]
    else:
        element_id = unmodified_list
        element = model_to_dict(model.objects.get(id = element_id ))
        unmodified_list = element[property]

    modified_list = unmodified_list
    return modified_list

def serialize_projects(profile):
    projects = profile.owned_projects.all()
    projects_serialized = projectsSerializer.ProjectSerializer(projects, many=True).data
    for project in projects_serialized:
        project["members"] = modify_property(models.Profiles, project["members"], "user_name")
        project["languages"] = modify_property(projectModels.Language, project["languages"], "name")
        project["owner"] = modify_property(models.Profiles, project["owner"] ,"user_name")
    return projects_serialized

def modify_username(comment):
    profile = models.Profiles.objects.get(id = comment["creater"])
    comment["creater"] = str(profile.user_name)
    return comment

def serialize_posts(posts, profile, viewer_profile):
    posts_list = []
    for post in posts:    
        post_dict = model_to_dict(post)
        comments = postSerializer.CommentSerializer(list(post.comments.all()), many=True).data
        post_dict["comments"] = [modify_username(comment) for comment in comments]
        likes = post.post_likes.count()
        post_dict["liked"] = False
        post_dict["postbox"] = {"user": f"{post.postbox.profile.first_name}  {post.postbox.profile.last_name}", "profile_picture":post.postbox.profile.profile_picture, "user_name": post.postbox.profile.user_name  }
        post_dict["timestamp"] = post.timestamp
        post_dict["is_owned"] = True if (profile.id==post.postbox.profile.id) else False
        for like in post.post_likes.all():
            if like.profile == viewer_profile:
                    print(profile.user_name)
                    post_dict["liked"] = True                  
        post_dict["likes"] = likes
        posts_list.append(post_dict)
    return posts_list