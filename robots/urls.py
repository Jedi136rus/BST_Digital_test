from django.contrib import admin
from django.urls import path
# from .views import api_posts
from .views import RobotsApi

urlpatterns = [
    # path('add/', api_posts),
    path('add/', RobotsApi.as_view()),
]
