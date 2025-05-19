from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChatListView.as_view(), name='chat_list'),
    path('create/<int:user_id>/', views.ChatRoomCreateView.as_view(), name='chat_create'),
    path('<int:pk>/', views.ChatRoomDetailView.as_view(), name='chat_detail'),
] 