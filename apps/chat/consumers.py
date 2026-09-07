import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        if not self.scope['user'].is_authenticated or not await self.is_participant():
            await self.close(code=4403)
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)
        body = payload.get('body', '').strip()
        if not body:
            return
        message = await self.save_message(body)
        await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': message})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def is_participant(self):
        return Conversation.objects.filter(id=self.conversation_id, participants=self.scope['user']).exists()

    @database_sync_to_async
    def save_message(self, body):
        message = Message.objects.create(conversation_id=self.conversation_id, sender=self.scope['user'], body=body)
        Conversation.objects.filter(id=self.conversation_id).update(updated_at=message.created_at)
        return {'id': message.id, 'body': body, 'sender': self.scope['user'].username,
                'sender_id': self.scope['user'].id, 'time': message.created_at.strftime('%H:%M')}