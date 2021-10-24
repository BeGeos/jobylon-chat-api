from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid


class User(AbstractUser):
    """
    Simple user class inheriting from the AbstractUser
    Added is_online status, but offers the possibility to add
    things later on in the project to scale
    """
    is_online = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.username


def get_uuid():
    """
    Create & return hexadecimal 32 characters UUIDs
    """
    return uuid.uuid4().hex


class Chat(models.Model):
    """
    A chat is where messages can be sent, it has 2 members

    The model auto-generates an id starting from 1,...
    For added security create a UUID field and use that as primary key
    """
    # if the user is deleted the chat is preserved
    id = models.CharField(primary_key=True, default=get_uuid, editable=False, max_length=32)
    timestamp = models.DateTimeField(auto_now_add=True)  # when the chat is created
    members = models.ManyToManyField(User, related_name="chat_member")
    messages = models.ManyToManyField("ChatMessage", related_name="chat")

    def __str__(self):
        return f"{self.id} - Chat"


# TODO A chat for groups could be implemented

class ChatMessage(models.Model):
    """
    Message class with author, content and timestamps
    """
    # if the user is deleted the message is preserved
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]  # set the order to date

    def __str__(self):
        return f"Chat Message - {self.id}"
