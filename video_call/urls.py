from django.urls import path
from . import views

app_name = 'video_call'

urlpatterns = [
    path('call/<str:room_name>/', views.video_call, name='video_call'),
] 