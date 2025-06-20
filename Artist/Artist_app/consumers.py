import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from .models import Room, Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        file_data = data.get('file')
        filename = data.get('filename')

        room = await sync_to_async(Room.objects.get)(name=self.room_name)

        if file_data and filename:
            format, filestr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file_content = ContentFile(base64.b64decode(filestr), name=filename)
            msg = await sync_to_async(Message.objects.create)(
                room=room,
                sender=self.user,
                file=file_content
            )
        else:
            msg = await sync_to_async(Message.objects.create)(
                room=room,
                sender=self.user,
                content=message
            )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg.content,
                'sender': self.user.username,
                'file_url': msg.file.url if msg.file else None,
                'file_ext': msg.file_extension() if msg.file else None,
                'timestamp': str(msg.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
