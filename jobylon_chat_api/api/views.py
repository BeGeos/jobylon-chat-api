from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import User, Chat, ChatMessage
from .serializer import UserSerializer, ChatSerializer

import json
import requests
import random

RANDOM_USER_API_URL = "https://random-data-api.com/api/users/random_user"


def home_view(request):
    """
    Home API view for documentation
    """
    return render(request, "documentation.html")


@api_view(["GET", "POST", "PUT", "DELETE"])
def not_found(request):
    return Response({
        "message": f"Page Not Found @ {request.get_full_path()}"
    }, status=404)


class UserView(APIView):
    """
    Views for users:
        * GET --> get all users
        * POST --> create a user
            * populate=<int> --> create <int> random users
    """

    def get(self, request, *args, **kwargs):
        """
        With id it fetches the user with that id OR 404
        """
        if "user_id" in self.kwargs.keys():
            try:
                user = User.objects.get(pk=self.kwargs["user_id"])
                serializer = UserSerializer(user, many=False)
                return Response(serializer.data, status=200)
            except User.DoesNotExist:
                return Response({
                    "message": "User not found"
                }, status=404)

        users = User.objects.filter(is_superuser=False)  # Get everyone but not admin or superusers
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        populate = request.GET.get("populate") in request.GET.getlist("populate")
        if populate:
            try:
                size = request.GET.get("populate") if int(request.GET.get("populate")) <= 100 else 100
                data = requests.get(RANDOM_USER_API_URL, params={"size": size})

                # Wipe out every user in DB, chat and messages will be not be deleted
                # But they will be inaccessible from any user --> it makes sense no user no chat no messages
                User.objects.filter(is_superuser=False).delete()
                for user in data.json():
                    username = user.get("username")
                    is_online = True if random.random() >= 0.5 else False  # 50% will be online
                    User.objects.create(username=username, is_online=is_online)
                return Response({
                    "message": f"{size} users created"
                }, status=201)
            except ValueError:
                return Response({
                    "message": "Populate must be an integer number"
                }, status=422)
            except Exception:
                return Response({
                    "message": "Something went wrong"
                }, status=500)

        data = request.data
        username = data.get("username", None)

        if not username:
            return Response({
                "message": "Username is required"
            }, status=400)

        # Check if already exists in the DB
        is_user = User.objects.filter(username=username).exists()

        if is_user:
            return Response({
                "message": "Username already in use"
            }, status=400)

        # If checks are OK save user to DB
        try:
            new_user = User.objects.create(username=username)
            new_user.save()
            serializer = UserSerializer(new_user, many=False)
            return Response(serializer.data, status=201)
        except Exception:
            return Response({
                "message": "Something went wrong"
            }, status=500)


class ChatView(APIView):
    """
    View for chats:
        * GET --> get the chat with id == chat_id [if not in members return 401]
        * POST --> send a message to chat [if not in members return 401]
    """
    def get(self, request, *args, **kwargs):
        user = request.GET.get("user", None)

        # To check if user belongs to the chat they want to see
        if not user:
            return Response({
                "message": "user params is required"
            }, status=401)

        # Look for chat with id --> chat_id
        chat = Chat.objects.filter(pk=self.kwargs.get("chat_id", None)).first()

        if not chat:
            return Response({
                "message": "Chat not found"
            }, status=404)

        if chat.members.filter(username=user).exists():
            serializer = ChatSerializer(chat)
            return Response(serializer.data, status=200)

        # If everything fails it means either user is not provided or
        # they don't belong to the chat
        # or the chat doesn't exist
        return Response({
            "message": "You are not part of this chat"
        }, status=401)

    def post(self, request, *args, **kwargs):
        """
        Since the is no authentication in the body of the request there will be a
        sender --> username who sends the message
        receiver --> username who receives the message
        content --> the actual message
        """
        data = request.data
        sender = data.get("sender", None)
        receiver = data.get("receiver", None)
        content = data.get("content", None)

        # Simple check to handle whether sender and receiver are the same
        if sender == receiver:
            return Response({
                "message": "If you want to talk to yourself, look in the mirror"
            }, status=400)

        if not sender or not receiver or not content:
            return Response({
                "message": "Sender, Receiver and Content are required"
            }, status=400)

        # Find the users
        from_user = User.objects.filter(username=sender).first()
        to_user = User.objects.filter(username=receiver).first()

        # Check if users exist
        is_user = from_user and to_user
        if not is_user:
            return Response({
                "message": "User not found"
            }, status=400)

        message = ChatMessage.objects.create(author=from_user, content=content)

        # Check if a chat with sender & receiver already exist if not create one
        # this check can be ambiguous because every chat with those 2 users will be picked
        # However, due to how the API is structured the Chat model will have only 2 members
        # For group chats there could be a dedicated model
        chat = Chat.objects.filter(members=from_user.id).filter(members=to_user.id).first()
        if chat:
            chat.messages.add(message)
            response = Chat.objects.get(pk=chat.id)
            serializer = ChatSerializer(response)
            return Response(serializer.data, status=201)

        # Create the chat
        chat = Chat.objects.create()
        chat.members.add(from_user, to_user)
        chat.messages.add(message)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=201)
