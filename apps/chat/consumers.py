import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        ''' Cliente se conecta '''

        # Recoge el nombre de la sala
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Se une a la sala
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Informa al cliente del éxito
        await self.accept()

    async def disconnect(self, close_code):
        ''' Cliente se desconecta '''
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        ''' Cliente envía información '''
        text_data_json = json.loads(text_data)
        text = text_data_json["text"]
        member_send = text_data_json["member_send"]
        member_receive = text_data_json["member_receive"]

        await self.save_message(member_send, member_receive, text)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "text": text,
                "member_send": member_send,
                "member_receive": member_receive,
            },
        )

    async def chat_message(self, event):
        ''' Recibe información de la sala '''
        text = event["text"]
        member_send = event["member_send"]
        member_receive = event["member_receive"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "text": text,
                    "member_send": member_send,
                    "member_receive": member_receive,
                }
            )
        )
