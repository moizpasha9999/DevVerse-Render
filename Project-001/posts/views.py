from django.shortcuts import render
from django.urls import reverse
from . import serializer
from profiles import models as Profilemodels
from . import models
from django.http import JsonResponse
import json
from django.forms.models import model_to_dict
from . import functions
from profiles import services
import base64



# Create your views here.
def render_post(request, p_id):
    post = models.Post.objects.get(id=p_id)
    post_dict = model_to_dict(post)
    viewer = base64.b64decode(request.GET.get("viewer"))
    viewer = viewer.decode("utf-8")
    print(viewer)
    viewer_profile = models.Profiles.objects.get(user_name=viewer)
    likes = post.post_likes.all()
    post_dict["liked"] = False
    comments = serializer.CommentSerializer(list(post.comments.all()), many=True).data
    post_dict["comments"] = [services.modify_username(comment) for comment in comments]
    for like in likes:
            if like.profile == viewer_profile:
                    post_dict["liked"] = True                  
    post_dict["likes"] = post.post_likes.count()
    post_dict["postbox"] = {"user": f"{post.postbox.profile.first_name}  {post.postbox.profile.last_name}", "profile_picture":post.postbox.profile.profile_picture  }
    
    return render(request, "profiles/post_template.html", {"p": post_dict})

def like_post(request):
    try:
        user_name = request.GET.get("user_name")
        post_id = request.GET.get("post_id")
        post = models.Post.objects.get(id=post_id)
        post_liked = models.Like.objects.get_or_create(post=post, profile=Profilemodels.Profiles.objects.get(user_name= user_name))[0]
        likes = len(list(post.post_likes.all()))

        return JsonResponse({"status":"success", "message": "Liked successfuly", "likes": likes  })

    except Exception as e:
            return JsonResponse({"status":"failed", "message": str(e)})




def edit_posts(request):
    try:
        data = json.loads(request.body)
        user_name = request.GET.get("user_name")
        password = request.GET.get("password")
        profile = Profilemodels.Profiles.objects.get(user_name= user_name)
        
        post = models.Post.objects.get(id=data["id"])
        if profile.password == password:
            if data.get("action") == "delete" and post.postbox.profile.id == profile.id:
               post.delete()
               return JsonResponse({"status":"success", "message": "Successful", "post": "deleted"})

            if data.get("comment"):
                print("here")
                profile = Profilemodels.Profiles.objects.get(user_name= data["user_name"])
                print("here")
                comment = serializer.CommentSerializer(data = {"content": data["comment"], "post": post.id, "creater": profile.id})
                print("there")
                if comment.is_valid():
                    comment = comment.save()
                    print(comment)
                else:
                    print(f"errors: {comment.errors}")

                return JsonResponse({"status":"success", "message": "Successful", "comment": model_to_dict(comment)})
            if data.get("shares"):

                data["shares"] = post.shares +1


            post_serialized = serializer.PostSerializer(post, data= data, partial=True)
            if post_serialized.is_valid():
                post = post_serialized.save()
                
                return JsonResponse({"status":"success", "message": "Successful", "post": model_to_dict(post)})
            else:
                print(f"errors: {post_serialized.errors}")
        else:
            return JsonResponse({"status":"failed", "message": "Unauthenticated"})
    except Exception as e:
         return JsonResponse({"status":"failed", "message": str(e)})


            


    

def get_posts(request):
    try:
        user_name = request.GET.get("user_name")
        password = request.GET.get("password")
        user_profile = Profilemodels.Profiles.objects.get(user_name=user_name)

        if password:
            if (user_profile.password==password):
                    models.PostBox.objects.get_or_create(profile=user_profile)
                    posts = user_profile.postbox.posts.all()
            else:
                return JsonResponse({"status":"failed", "message": "Unauthenticated"})

        else:
            posts = models.Post.objects.exclude(
                     postbox__profile__blacklist=user_profile
                )
        posts_list = services.serialize_posts(posts, user_profile, user_profile)
        print("mai hi hu")

        return JsonResponse({"status":"success", "message": "Successful", "posts": list(reversed(posts_list))})


        
    except Exception as e:
            return JsonResponse({"status":"failed", "message": str(e)})

def create_post(request):
    try:
        data = {**request.POST, **request.FILES}
        for key,value in data.items(): data[key] = value[0]
        
        print(data)
        print(type(data))
        profile = Profilemodels.Profiles.objects.get(user_name=data["user_name"])

        if (profile.password==data["password"]):

            postBox = models.PostBox.objects.get_or_create(profile=profile)[0]

            post = serializer.PostSerializer(data={
            "payload": data["text"],
            "postbox": postBox.id,
            "likes": data["likes"],
            "shares": data["shares"],
            "image" : data["image"]
        })
            if post.is_valid():
                post = post.save()
                response_data = serializer.PostSerializer(post).data
            else:
                print(post.errors)
        
            return JsonResponse({"status":"success", "message": "Created", "post": response_data})
        
        else:
            return JsonResponse({"status":"failed", "message": "Unauthenticated"})
    except Exception as e:
            return JsonResponse({"status":"failed", "message": str(e)})
