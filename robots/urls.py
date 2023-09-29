from django.contrib import admin
from django.urls import path
# from .views import api_posts
from .views import RobotsApi, excel_report

urlpatterns = [
    # path('add/', api_posts),
    path('add/', RobotsApi.as_view()),
    path('excel_report/', excel_report)
]
