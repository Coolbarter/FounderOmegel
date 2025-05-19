from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

# Create your views here.

class ChatListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/chat_list.html'
    context_object_name = 'chat_rooms'

    def get_queryset(self):
        chat_rooms = ChatRoom.objects.filter(
            participants=self.request.user
        ).order_by('-created_at')
        
        # Add other_user to each chat room
        for chat_room in chat_rooms:
            chat_room.other_user = chat_room.participants.exclude(id=self.request.user.id).first()
        
        return chat_rooms

class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'chat/chat_detail.html'
    context_object_name = 'chat_room'

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat_room = self.get_object()
        context['messages'] = chat_room.messages.all().order_by('created_at')
        context['other_user'] = chat_room.participants.exclude(id=self.request.user.id).first()
        return context

    def post(self, request, *args, **kwargs):
        chat_room = self.get_object()
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=content
            )
        return redirect('chat_detail', pk=chat_room.pk)

class ChatRoomCreateView(LoginRequiredMixin, CreateView):
    model = ChatRoom
    template_name = 'chat/chat_room_form.html'
    success_url = reverse_lazy('chat_list')

    def get(self, request, *args, **kwargs):
        other_user_id = kwargs.get('user_id')
        if not other_user_id:
            messages.error(request, "No user specified")
            return redirect('chat_list')
        
        other_user = get_object_or_404(User, id=other_user_id)
        
        # Check if a chat room already exists between these users
        existing_chat = ChatRoom.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).first()
        
        if existing_chat:
            return redirect('chat_detail', pk=existing_chat.pk)
        
        # Create a new chat room
        chat_room = ChatRoom.objects.create(
            room_name=f"chat_{request.user.id}_{other_user.id}"
        )
        chat_room.participants.add(request.user, other_user)
        
        messages.success(request, "Chat room created successfully!")
        return redirect('chat_detail', pk=chat_room.pk)
