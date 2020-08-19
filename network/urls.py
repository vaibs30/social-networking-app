
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("all_posts", views.all_posts, name="all_posts"),
    path("following_posts", views.following_posts, name="following_posts"),
    path("profile/<str:profile_user>", views.profile,name="profile"),
    path("profile_page", views.profile_page,name="profile_page"),
    path("follow", views.follow,name="follow"),
    path("like", views.like,name="like"),
]
