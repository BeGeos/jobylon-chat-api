from rest_framework import serializers
from .models import User, Chat, ChatMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "is_online", "date_joined"]


class ChatMessageListing(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = ChatMessage
        exclude = ["id"]


class ChatSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        read_only=True
    )
    messages = ChatMessageListing(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "timestamp", "members", "messages"]

