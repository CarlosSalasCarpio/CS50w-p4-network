
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"),
    path("delete_post/<int:post_id>", views.delete_post, name="delete_post"),  
    path("user_profile/<str:user>", views.user_profile, name="user_profile"),
    path("follow/<str:user>", views.follow, name="follow"),
    path("unfollow/<str:user>", views.unfollow, name="unfollow"),

    # API Routes
    path("posts", views.posts, name="posts"),
    path("like_post_api/<int:post_id>", views.like_post_api, name="like_post_api"),
    path("edit_post_api/<int:post_id>/<str:post_body>", views.edit_post_api, name="edit_post_api"),
]
