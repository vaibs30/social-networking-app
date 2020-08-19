import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    post_list = Post.objects.all()
    post_list = post_list.order_by("-timestamp").all()
    page = request.GET.get('page', 1)
    post_list = [post.serialize() for post in post_list]
    for post in post_list:
        for liker in post["likers"]:
            if liker == request.user.username:
                post.update({'liked':'true'}) 
        print(post)
    paginator = Paginator(post_list, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'network/index.html', { 'posts': posts })

@csrf_exempt
def all_posts(request):
    post_list = Post.objects.all()
    post_list = post_list.order_by("-timestamp").all()
    page = request.GET.get('page', 1)
    post_list = [post.serialize() for post in post_list]
    paginator = Paginator(post_list, 2)
    try:
        posts = list(paginator.page(page))
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return JsonResponse(posts, safe=False)        

def following_posts(request):
    active_user = User.objects.get(username = request.user)
    profile_data = active_user.serialize()
    following_users = profile_data["following"]
    list_ids = []
    for following in following_users:
        user_obj = User.objects.get(username = following)
        posts_obj = Post.objects.filter(poster = user_obj)
        for post in posts_obj:
            list_ids.append(post.id)
    post_list = Post.objects.filter(id__in = list_ids)
    post_list = post_list.order_by("-timestamp").all()
    post_list = [post.serialize() for post in post_list]
    for post in post_list:
        for liker in post["likers"]:
            if liker == request.user.username:
                post.update({'liked':'true'})
    page = request.GET.get('page', 1)

    paginator = Paginator(post_list, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'network/following.html', { 'posts': posts })

@csrf_exempt
@login_required
def profile(request, profile_user):
    profile_user = User.objects.get(username = profile_user)
    print(profile_user)
    post_list = Post.objects.filter(user = profile_user )
    post_list = post_list.order_by("-timestamp").all()
    post_list = [post.serialize() for post in post_list]
    for post in post_list:
        for liker in post["likers"]:
            if liker == request.user.username:
                post.update({'liked':'true'})
    page = request.GET.get('page', 1)

    paginator = Paginator(post_list, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'network/profile.html', { 'posts': posts, 'profile_user' : profile_user })

@csrf_exempt
@login_required
def profile_page(request):
        
    # Check post body
    if request.method == "POST":
        data = json.loads(request.body)

        # Get contents of post
        user = data.get("body", "")
        print(user)
        # Filter user details
        profile_user = User.objects.get(username = user)
        profile_data = profile_user.serialize()
        posts = Post.objects.filter(user = profile_user)
        post_data = [post.serialize() for post in posts]
        data = [profile_data, post_data]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Only POST OR PUT methods allowed"}, status=400)

@csrf_exempt
@login_required
def follow(request):
    
    # Check post body
    if request.method == "POST":
        data = json.loads(request.body)

        # Get contents of post
        user = data.get("body", "")
        action = data.get("action", "")
        
        # perform action
        if action == "followUser":
            follow_user = User.objects.get(username = user)
            active_user = User.objects.get(username = request.user)
            follow_user.followers.add(active_user)
            follow_user.save()
            active_user.following.add(follow_user)
            active_user.save()
            return JsonResponse({"message": "successful"}, safe=False)
        elif action == "unfollowUser":
            follow_user = User.objects.get(username = user)
            active_user = User.objects.get(username = request.user)
            follow_user.followers.remove(active_user)
            follow_user.save()
            active_user.following.remove(follow_user)
            active_user.save()
            return JsonResponse({"message": "successfully unfollowed"}, safe=False)
    else:
        return JsonResponse({"error": "Only POST OR PUT methods allowed"}, status=400)

@csrf_exempt
@login_required
def new_post(request):

    # Check post body
    if request.method == "POST":
        data = json.loads(request.body)

        # Get contents of post
        body = data.get("body", "")

        # Create one post
        post = Post(
                user=request.user,
                poster=request.user,
                body=body,
                    )
        post.save()
        return JsonResponse({"message": "Posted successfully."}, status=201)
    else:
        return render(request, 'network/new_post.html')

@csrf_exempt
@login_required
def edit_post(request):
    print(request.method)
    # Check post body
    if request.method == "POST":
        data = json.loads(request.body)

        # Get contents of post
        body = data.get("body", "")
        post_id = data.get("id", "")

        post = Post.objects.get(id = post_id)
        post.body = body
        post.save()
        return JsonResponse({"message": "Post edited successfully."}, status=201)
    elif request.method == "GET":
        post_id = request.headers["X-Custom-Header"]
        post = Post.objects.get(id = post_id)
        post = post.serialize()
        return JsonResponse(post, status=201)

@csrf_exempt
@login_required
def like(request):
        
    # Check post body
    if request.method == "POST":
        data = json.loads(request.body)

        # Get contents of post
        post_id = data.get("post_id", "")
        action = data.get("action", "")
        
        # perform action
        if action == "like":
            active_user = User.objects.get(username = request.user)
            post = Post.objects.get(id = post_id)
            post.likers.add(active_user)
            post.save()
            return JsonResponse({"message": "successfully liked"}, safe=False)
        elif action == "unlike":
            active_user = User.objects.get(username = request.user)
            post = Post.objects.get(id = post_id)
            post.likers.remove(active_user)
            post.save()
            return JsonResponse({"message": "successfully unliked"}, safe=False)
    else:
        return JsonResponse({"error": "Only POST OR PUT methods allowed"}, status=400)

@csrf_exempt
@login_required
def edit(request, post_id):
    return render(request, 'network/edit_post.html', {'post_id' : post_id})


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
