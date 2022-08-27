import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count
from django.views.generic import ListView
from django.core.paginator import Paginator

from .models import User, PostModel

class PostListView(ListView):
    paginate_by: 2
    model = PostModel


def index(request):
    # Render all post from all users ordered by the newest to the oldest
    posts = PostModel.objects.annotate(number_of_likes=Count('likes', distinct=True)).order_by('-created_at')

    # Paginate the posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        'page_obj': page_obj,
    })


# Shows the user's profile
@login_required
def user_profile(request, user):
    # Get the posts created by that user and the number of followers/followings
    posts = PostModel.objects.filter(created_by = user).annotate(number_of_likes=Count('likes', distinct=True)).order_by('-created_at')
    print(posts)
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the number of followers/followings
    following = User.objects.get(pk = user).following.all().count()
    followers = User.objects.get(pk = user).followers.all().count()

    # Check if the user already follows the user of the profile visited
    already_follows = User.objects.get(pk = request.user.id).following.all().filter(id = user).exists()

    print('already_follows: ' + str(already_follows))
    print('request.user.id: ' + str(request.user.id))

    profile_owner = str(user) == str(request.user.id)

    return render(request, "network/user_profile.html", {
        'user': User.objects.get(pk = user),
        'page_obj': page_obj,
        'following': following,
        'followers': followers,
        'already_follows': already_follows,
        'profile_owner': profile_owner
    })    

@login_required
def following(request):
    # # Get the posts created by the users being followed
    followers = User.objects.filter(pk = request.user.id).values('following__id')
    posts = PostModel.objects.annotate(number_of_likes=Count('likes', distinct=True)).filter(created_by__in = followers).order_by('-created_at')

    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        'page_obj': page_obj,
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


@login_required
# This function creates new posts
def create_post(request):
    if request.method == "POST":
        # Get post's body from the textarea
        body = request.POST["post-body"]

        # Creates a set that only contains the user that creates the post
        users = set()
        users.add(request.user)
        for user in users:
            user = user

        # Creates the post
        post = PostModel(
            body = body,
            created_by = user
            )
        post.save()
        return HttpResponseRedirect(reverse("index"))    


@login_required
# This function deletes an existing new posts
def delete_post(request, post_id):
    if request.method == "POST":  
        PostModel.objects.filter(id = post_id).delete()
        return HttpResponseRedirect(reverse("index"))


@login_required
# Follow an active user
def follow(request, user):
    if request.method == "POST":      
        User.objects.get(pk = request.user.id).following.add(user)
        return HttpResponseRedirect(reverse("user_profile", args=(user,)))


@login_required
# Unfollow an active user
def unfollow(request, user):
    if request.method == "POST":      
        User.objects.get(pk = request.user.id).following.remove(user)
        return HttpResponseRedirect(reverse("user_profile", args=(user,)))


# API ROUTES

# An API with all the posts
@csrf_exempt
def posts(request):  
    posts = PostModel.objects.order_by("-created_at").all()
    return JsonResponse([post.serialize() for post in posts], safe=False)


# Likes API
@csrf_exempt
@login_required
def like_post_api(request, post_id):

    try:
        post = PostModel.objects.get(pk = post_id)
    except:
        return JsonResponse({
            "error": "error: Post not found."
        }, status=404)

    if post.likes.filter(pk = request.user.id).exists():
        post.likes.remove(request.user.id)
        return JsonResponse(post.serialize())
    else:
        post.likes.add(request.user.id)
        return JsonResponse(post.serialize())


# Edit API
@csrf_exempt
@login_required
def edit_post_api(request, post_id, post_body):

    try:
        post = PostModel.objects.get(pk = post_id)
    except:
        return JsonResponse({
            "error": "error: Post not found."
        }, status=404)

    if post.created_by_id != request.user.id:
        return JsonResponse({
            "error": "You don't have acceess to this post."
        }, status=404)
    else:
        post.body = post_body
        post.save()

        return JsonResponse(post.serialize())