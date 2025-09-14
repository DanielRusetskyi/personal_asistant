import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("noteapp.ws")


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            logger.debug("WS connect: anonymous -> close")
            await self.close()
            return

        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.debug("WS connected: user=%s channel=%s group=%s",
                     user.id, self.channel_name, self.group_name)

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.debug("WS disconnected: group=%s code=%s", self.group_name, code)
    # ІМ’Я МЕТОДУ МАЄ СПІВПАСТИ з "type" у group_send -> "notify"

    async def notify(self, event):
        payload = event.get("payload", {})
        logger.debug("WS notify -> send to client: %s", payload)
        await self.send(text_data=json.dumps(payload))
