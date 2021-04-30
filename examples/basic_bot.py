from dogehouse import DogeClient
from dogehouse.entities import MessageEvent, ReadyEvent, RoomJoinEvent, UserJoinEvent


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


@doge.on_user_join
async def greet_user(event: UserJoinEvent) -> None:
    await doge.send_message(f"Hello @{event.user.username}")


@doge.on_message
async def echo(event: MessageEvent) -> None:
    await doge.send_message(f'@{event.message.author} said {event.message.content}')


doge.run()
