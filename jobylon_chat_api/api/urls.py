from django.urls import path, re_path
from .views import UserView, ChatView, home_view, not_found

urlpatterns = [
    path("", home_view, name="API-home"),
    path("users", UserView.as_view(), name="get-all-users"),
    path("users/<int:user_id>", UserView.as_view(), name="get-user"),
    path("chat", ChatView.as_view(), name="init-chat"),
    path("chat/<str:chat_id>", ChatView.as_view(), name="chat"),
    re_path(r"^.*/$", not_found, name="Not-Found")
]
