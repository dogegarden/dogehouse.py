import os
from dogehouse.events import ReadyEvent, RoomJoinEvent, UserJoinEvent, MessageEvent, MessageDeleteEvent, ChatMemberEvent
from dogehouse import DogeClient

token = os.getenv("TOKEN", '')
refresh_token = os.getenv("REFRESH_TOKEN", '')

doge = DogeClient(token, refresh_token)

banned_words = ['bad']
severe_words = ['racist']
user_infractions = {}

@doge.on_ready
async def ready(event: ReadyEvent) -> None:
    print('Bot is up!')
    await doge.create_room('Auto-moderation')

@doge.on_room_join
async def room_join(event: RoomJoinEvent) -> None:
    pass

@doge.on_user_join
async def user_join(event: UserJoinEvent) -> None:
    user_infractions[event.user.id] = dict(infractions=0)

@doge.on_message
async def message(event: MessageEvent) -> None:
    msg = event.message

    for word in banned_words:
        if word in msg.content:
            if user_infractions[msg.author.id]['infractions'] > 2:
                await doge.ban_chat_user(msg.author.id)
            else:
                await doge.delete_message(msg)
                user_infractions[msg.author.id]['infractions'] += 1

    for word in severe_words:
        if word in msg.content:
            await doge.ban_room_user(msg.author.id)

@doge.on_message_deleted
async def message_deleted(event: MessageDeleteEvent) -> None:
    await doge.send_message(f'Deleted message: {event.message_id} from {event.author_id}')

@doge.on_chat_member_banned
async def chat_member_banned(event: ChatMemberEvent) -> None:
    await doge.send_message(f'Chat-Banned {event.chat_member.id}')

doge.run()
