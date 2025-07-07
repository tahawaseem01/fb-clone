import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.recipient_id = self.scope['url_route']['kwargs']['recipient_id']
        self.user = self.scope['user']
        self.room_group_name = f"chat_{min(self.user.id, int(self.recipient_id))}_{max(self.user.id, int(self.recipient_id))}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        print(f"📨 Received message via WebSocket: {message}")

        recipient = await self.get_recipient(int(self.recipient_id))

        # Save to DB
        await self.save_message(self.user, recipient, message)
        print(f"📣 Creating notification for: {recipient}")

        # Create notification
        await self.create_notification(self.user, recipient)

        # Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def get_recipient(self, recipient_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.get(id=recipient_id)

    @database_sync_to_async
    def save_message(self, sender, recipient, content):
        from .models import Message
        return Message.objects.create(sender=sender, recipient=recipient, content=content)

    @database_sync_to_async
    def create_notification(self, sender, recipient):
        from .models import Notification  # adjust if in another app
        from django.urls import reverse
        try:
            print("✅ Notification being created")
            return Notification.objects.create(
                recipient=recipient,
                sender=sender,
                verb="sent you a message",
                url=reverse('message_user', args=[sender.id])
           ) 
        except Exception as e:
            print(f"❌ Failed to create notification: {e}")