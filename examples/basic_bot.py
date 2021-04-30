import logging

from dogehouse import DogeClient
from dogehouse.entities import Event, MessageEvent, ReadyEvent, RoomJoinEvent

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


token = "your user token"
refresh_token = "refresh token"

doge = DogeClient(token, refresh_token)


@doge.on_ready
async def make_my_room(event: ReadyEvent) -> None:
    print(f"Successfully connected as @{event.user.username}!")
    await doge.create_room("Hello World!")


@doge.on_room_join
async def joined_room(event: RoomJoinEvent) -> None:
    print("Joined room", event.room.name)


@doge.on_message
async def echo(event: MessageEvent) -> None:
    await doge.send_message(f'@{event.message.author} said {event.message.content}')


doge.run()
