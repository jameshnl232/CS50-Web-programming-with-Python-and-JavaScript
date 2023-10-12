from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator




from .models import User, Post, Like


def index(request):
    posts = Post.objects.order_by("-timestamp").all()
    paginator = Paginator(posts,10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def user_page(request, username):

    user = get_object_or_404(User, username=username)
    current_user = request.user

    user_posts = user.user_posts.order_by("-timestamp").all()
    paginator = Paginator(user_posts,10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    if request.method == "POST":
    # check the status
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        
        status = request.POST['follow-button']
        if status == 'Unfollow':
            user.followers.remove(current_user)
            current_user.unfollow(user)
        elif status == 'Follow':
            user.followers.add(current_user)
            current_user.follow(user)   
        pass

    if current_user in user.followers.all():
        follow_text = "Unfollow"
    else:
        follow_text = "Follow"
            

    return render(request, "network/userPage.html", {
        "user": user,
        "posts": page_obj,
        "follow_unfollow": follow_text
    })


def following(request):
    following = request.user.following.all()
    posts = Post.objects.filter(user__in=following).order_by("-timestamp")

    paginator = Paginator(posts,10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": page_obj
    })



#API routes
@csrf_exempt
@login_required
def new_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # check new post
    data = json.loads(request.body)

    content = data.get("content", "")

    post = Post(
        user=request.user,
        content=content
    )
    post.save()
    return JsonResponse({"message": "Created new post"}, status=201)

@csrf_exempt
@login_required
def get_post(request, id):
    try: 
        post = Post.objects.get(pk=id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    # Return email contents
    if request.method == "GET":
        return JsonResponse(post.serialize())
    
    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]   
            post.save()
        return JsonResponse({
            "edited": True,
        })
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

@csrf_exempt
@login_required
def toggle_like(request, post_id):
    try: 
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "POST":
             #user who likes post            
        if request.user not in post.likes.all() :
            post.likes.add(request.user)
        else:
            post.likes.remove(request.user)
        post.save()
        return JsonResponse({
            "like_count": post.likes.count(),
            "like_status": request.user in post.likes.all() 
        })
    





    