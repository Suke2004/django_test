from django.urls import path
from .views import ChatAPIView, home

urlpatterns = [
    path("", home),
    path("chat/", ChatAPIView.as_view()),
]
