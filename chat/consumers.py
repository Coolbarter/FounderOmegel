import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import ChatRoom, Message

logger = logging.getLogger(__name__)
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            self.user = self.scope['user']

            if not self.user.is_authenticated:
                logger.warning(f"Unauthenticated user attempted to connect to room {self.room_name}")
                await self.close(code=4001)
                return

            # Verify chat room exists
            try:
                self.chat_room = await self.get_chat_room()
            except ObjectDoesNotExist:
                logger.error(f"Chat room {self.room_name} does not exist")
                await self.close(code=4004)
                return

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"User {self.user.email} connected to chat room {self.room_name}")

            # Notify others in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.email
                }
            )
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close(code=4000)
            raise StopConsumer()

    async def disconnect(self, close_code):
        try:
            logger.info(f"User {self.user.email} disconnecting from room {self.room_name}")
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            # Notify others about departure
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.email
                }
            )
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'webrtc_signal':
                await self.handle_webrtc_signal(text_data_json)
            else:
                logger.warning(f"Received unknown message type: {message_type}")
        except json.JSONDecodeError:
            logger.error("Received invalid JSON data")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    async def handle_chat_message(self, data):
        message = data['message']
        user = self.scope['user']

        # Save message to database
        await self.save_message(user, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.email
            }
        )

    async def handle_webrtc_signal(self, data):
        # Forward WebRTC signaling data to other peer
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_signal',
                'signal': data['signal'],
                'user': self.scope['user'].email
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user': event['user']
        }))

    async def webrtc_signal(self, event):
        # Send WebRTC signal to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'signal': event['signal'],
            'user': event['user']
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        chat_room = ChatRoom.objects.get(room_name=self.room_name)
        Message.objects.create(
            chat_room=chat_room,
            sender=user,
            content=message
        )

    @database_sync_to_async
    def get_chat_room(self):
        return ChatRoom.objects.get(room_name=self.room_name)

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user': event['user']
        }))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user': event['user']
        }))