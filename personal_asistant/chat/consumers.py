# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils.html import strip_tags
from .models import Thread, ThreadMember, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.group_name = f"chat_{self.thread_id}"

        if not await self.user_in_thread():
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def user_in_thread(self):
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False

        try:
            t = Thread.objects.get(pk=self.thread_id, is_archived=False)
        except Thread.DoesNotExist:
            return False
        return t.members.filter(user=user).exists()
        # return ThreadMember.objects.filter(thread_id=self.thread_id, user=user).exists()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            payload = json.loads(text_data or "{}")
        except Exception:
            return

        content = (payload.get("content") or "").strip()   # <-- content
        if not content:
            return
        if len(content) > 4000:
            content = content[:4000]

        msg = await self.save_message(content)

        await self.channel_layer.group_send(self.group_name, {
            "type": "chat.message",
            "id": msg["id"],
            "user_id": msg["user_id"],
            "user_name": msg["user_name"],
            "content": msg["content"],       # <-- content
            "created": msg["created"],
        })

    @database_sync_to_async
    def save_message(self, content):
        user = self.scope["user"]
        m = Message.objects.create(
            thread_id=self.thread_id,
            user=user,
            content=strip_tags(content),     # <-- content
        )
        return {
            "id": m.id,
            "user_id": m.user_id,
            "user_name": getattr(user, "username", str(user)),
            "content": m.content,            # <-- content
            "created": m.created.isoformat(),
        }

    async def chat_message(self, event):
        # подія вже має ключ "content"
        await self.send(text_data=json.dumps(event))
