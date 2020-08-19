from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("User", related_name="followers_user")
    following = models.ManyToManyField("User", related_name="following_user")
    
    def serialize(self):
        return {
            "username" : self.username,
            "followers": [user.username for user in self.followers.all()],
            "following": [user.username for user in self.following.all()],
        }

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    poster = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posted_by")
    body = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    likers = models.ManyToManyField("User", related_name="likers")

    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster.username,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
            "likers": [user.username for user in self.likers.all()],
        }
