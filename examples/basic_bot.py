import os

from dogehouse import DogeClient
from dogehouse.events import (
    ReadyEvent, RoomsFetchedEvent, RoomJoinEvent,
    MessageEvent, UserJoinEvent, UserLeaveEvent,
    MessageDeleteEvent, ChatMemberEvent,
)

token = os.getenv("TOKEN", '')
refresh_token = os.getenv("REFRESH_TOKEN", '')

doge = DogeClient(token, refresh_token)

banned_words = ['hack', 'spoof']
severe_words = ['racist']

@doge.on_ready
async def make_my_room(event: ReadyEvent) -> None:
    print(f"Successfully connected as @{event.user.username}!")


@doge.on_rooms_fetch
async def join_any_room(event: RoomsFetchedEvent) -> None:
    await doge.create_room('Hello dogehouse.py!')


@doge.on_room_join
async def joined_room(event: RoomJoinEvent) -> None:
    print("Joined room", event.room.name)


@doge.on_user_join
async def greet_user(event: UserJoinEvent) -> None:
    await doge.send_message(f"Hello @{event.user.username}")
    await doge.send_message(f"Hi, I sent you a whisper!", whisper_to=[event.user])


@doge.on_user_leave
async def user_left(event: UserLeaveEvent) -> None:
    await doge.send_message(f"Bye @{event.user.username}")


@doge.on_message
async def echo_message(event: MessageEvent) -> None:
    msg = event.message

    # Simple automod
    for word in banned_words:
        if msg.content.count(word):
            await doge.delete_message(msg)

    for word in severe_words:
        if msg.content.count(word):
            await doge.chat_ban_user(msg.author.id) # same for chat_unban_user

@doge.on_chat_member_banned
async def chat_member_banned(event: ChatMemberEvent):
    await doge.send_message(f'Chat-Banned user: {event.chat_member.id}')

@doge.on_message_deleted
async def message_deleted(event: MessageDeleteEvent) -> None:
    await doge.send_message(f'Deleted message: {event.message_id}')

@doge.command
async def echo(event: MessageEvent) -> None:
    msg = event.message
    await doge.send_message(f'@{msg.author.username} said {msg.content}')

doge.run()
