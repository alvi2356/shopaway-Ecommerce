import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatSession, ChatMessage, ChatNotification
from django.utils import timezone
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality.
    Handles WebSocket connections, message broadcasting, and database operations.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.session_key = self.scope['url_route']['kwargs']['session_key']
        self.room_group_name = f'chat_{self.session_key}'

        # Join room group for this chat session
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        print(f"🔌 WebSocket connected for session: {self.session_key}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"🔌 WebSocket disconnected for session: {self.session_key}")

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        This method processes messages sent directly through WebSocket.
        """
        try:
            data = json.loads(text_data)
            message = data['message']
            is_staff_reply = data.get('is_staff_reply', False)
            session_key = self.session_key

            print(f"📨 WebSocket received message: {message} (Staff: {is_staff_reply})")

            # Save message to database
            await self.save_message(session_key, message, is_staff_reply)

            # Broadcast message to all clients in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'is_staff_reply': is_staff_reply,
                    'timestamp': str(timezone.now()),
                }
            )
            
        except Exception as e:
            print(f"❌ Error processing WebSocket message: {e}")

    async def chat_message(self, event):
        """
        Handle chat messages broadcasted to the room group.
        This method sends messages to all connected WebSocket clients.
        """
        print(f"📨 Broadcasting message to WebSocket clients:")
        print(f"   Message: {event['message']}")
        print(f"   Is staff reply: {event['is_staff_reply']}")
        print(f"   Timestamp: {event['timestamp']}")
        print(f"   Room: {self.room_group_name}")
        
        # Send message to WebSocket client
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'is_staff_reply': event['is_staff_reply'],
            'timestamp': event['timestamp'],
            'message_id': event.get('message_id'),
        }))
        
        print(f"✅ Message sent to WebSocket client")

    @database_sync_to_async
    def save_message(self, session_key, message, is_staff_reply):
        """
        Save message to database asynchronously.
        This method handles database operations for message storage.
        """
        try:
            session = ChatSession.objects.get(session_key=session_key)
            
            # Create and save the message
            chat_message = ChatMessage.objects.create(
                session=session, 
                message=message, 
                is_staff_reply=is_staff_reply
            )
            
            print(f"💾 Message saved to database: {message}")
            
            # Create notifications for staff if it's a user message
            if not is_staff_reply:
                staff_users = User.objects.filter(is_staff=True)
                for staff_user in staff_users:
                    ChatNotification.objects.get_or_create(
                        session=session,
                        staff_user=staff_user,
                        defaults={'is_read': False}
                    )
                print(f"📧 Notifications created for {staff_users.count()} staff users")
                
        except ChatSession.DoesNotExist:
            print(f"❌ Chat session not found: {session_key}")
        except Exception as e:
            print(f"❌ Error saving message: {e}")