from django.contrib import admin
from .models import User, Chat, ChatMessage

admin.site.register(User)
admin.site.register(Chat)
admin.site.register(ChatMessage)