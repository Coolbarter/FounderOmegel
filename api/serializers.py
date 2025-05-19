from rest_framework import serializers
from accounts.models import User
from profiles.models import FounderProfile
from matchmaking.models import Match
from chat.models import ChatRoom, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_verified', 'created_at')
        read_only_fields = ('is_verified', 'created_at')

class FounderProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FounderProfile
        fields = (
            'id', 'user', 'company_name', 'industry', 'stage', 'description',
            'website', 'linkedin', 'twitter', 'profile_picture', 'interests',
            'looking_for', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

class MatchSerializer(serializers.ModelSerializer):
    founder1_profile = FounderProfileSerializer(source='founder1.founder_profile', read_only=True)
    founder2_profile = FounderProfileSerializer(source='founder2.founder_profile', read_only=True)

    class Meta:
        model = Match
        fields = (
            'id', 'founder1', 'founder2', 'founder1_profile', 'founder2_profile',
            'status', 'match_score', 'common_interests', 'created_at',
            'updated_at', 'scheduled_time', 'notes'
        )
        read_only_fields = ('founder1', 'founder2', 'match_score', 'common_interests', 'created_at', 'updated_at')

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'chat_room', 'sender', 'content', 'timestamp', 'is_system_message')
        read_only_fields = ('timestamp', 'is_system_message')

class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    match = MatchSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ('id', 'match', 'room_name', 'is_active', 'messages', 'created_at', 'updated_at')
        read_only_fields = ('room_name', 'created_at', 'updated_at') 