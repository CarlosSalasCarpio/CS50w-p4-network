from xml.dom.minidom import CharacterData
from django.contrib.auth.models import AbstractUser
from django.db import models
from requests import request


class User(AbstractUser):
    pass
    following = models.ManyToManyField("self", blank=True, related_name='followers', symmetrical=False)

class PostModel(models.Model):
    body = models.CharField(max_length=280)
    likes = models.ManyToManyField("User", blank=True, related_name='likes', symmetrical=False)
    created_by = models.ForeignKey("User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "body": self.body,
            "created_by": self.created_by.username,
            "created_at": self.created_at,
            "likes_number": self.likes.count(),
            "liked_by": [user.id for user in self.likes.all()]
        }