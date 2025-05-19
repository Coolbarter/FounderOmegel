import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)
User = get_user_model()

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'video_call_{self.room_name}'
            self.user = self.scope['user']
            
            logger.info(f"Attempting to connect user {self.user.username} to room {self.room_name}")
            
            if not self.user.is_authenticated:
                logger.warning(f"Unauthenticated user tried to connect to room {self.room_name}")
                await self.close(code=4001)
                return
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"User {self.user.username} connected to video call room {self.room_name}")
            
            # Notify others in the room that a new user joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.user.username,
                    'room': self.room_name
                }
            )
            
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            if hasattr(self, 'close'):
                await self.close()
            raise

    async def disconnect(self, close_code):
        try:
            logger.info(f"User {self.user.username} disconnecting from room {self.room_name}")
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Notify others that user has left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': self.user.username,
                    'room': self.room_name
                }
            )
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            # Add sender information to all messages
            text_data_json['sender'] = self.user.username
            
            if message_type == 'offer':
                await self.handle_offer(text_data_json)
            elif message_type == 'answer':
                await self.handle_answer(text_data_json)
            elif message_type == 'candidate':
                await self.handle_candidate(text_data_json)
            else:
                logger.warning(f"Received unknown message type: {message_type}")
        
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    async def handle_offer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_offer',
                'offer': data['offer'],
                'sender': data['sender']
            }
        )

    async def handle_answer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_answer',
                'answer': data['answer'],
                'sender': data['sender']
            }
        )

    async def handle_candidate(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_candidate',
                'candidate': data['candidate'],
                'sender': data['sender']
            }
        )

    # Handlers for messages from room group
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'room': event['room']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'room': event['room']
        }))

    async def send_offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer'],
            'sender': event['sender']
        }))

    async def send_answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer'],
            'sender': event['sender']
        }))

    async def send_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'candidate',
            'candidate': event['candidate'],
            'sender': event['sender']
        }))