from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import User
from profiles.models import FounderProfile
from matchmaking.models import Match
from chat.models import ChatRoom, Message
from .serializers import (
    UserSerializer, FounderProfileSerializer, MatchSerializer,
    MessageSerializer, ChatRoomSerializer
)

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

class FounderProfileViewSet(viewsets.ModelViewSet):
    queryset = FounderProfile.objects.all()
    serializer_class = FounderProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FounderProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(founder1=self.request.user) | Match.objects.filter(founder2=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        match = self.get_object()
        if match.founder2 == request.user:
            match.status = 'accepted'
            match.save()
            return Response({'status': 'match accepted'})
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        match = self.get_object()
        if match.founder2 == request.user:
            match.status = 'rejected'
            match.save()
            return Response({'status': 'match rejected'})
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(match__founder1=self.request.user) | ChatRoom.objects.filter(match__founder2=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat_room = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=content
        )
        return Response(MessageSerializer(message).data)

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            chat_room__match__founder1=self.request.user
        ) | Message.objects.filter(
            chat_room__match__founder2=self.request.user
        )
