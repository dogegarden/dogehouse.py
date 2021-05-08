from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import DogeClient

from .entities import (
    ApiData, Message, Room, RoomPreview,
    User, UserPreview, ChatMember, RoomMember
)
from .events import (
    ReadyEvent, MessageEvent,
    RoomsFetchedEvent, RoomJoinEvent,
    UserJoinEvent, UserLeaveEvent,
    MessageDeleteEvent, ChatMemberEvent,
    RoomMemberEvent, FetchRoomBannedUsersEvent,
    StateEvent, HandRaisedEvent, CommandEvent,
)
from .util import parse_tokens_to_message


############################# Data Parsers #############################

def parse_user(user_dict: ApiData) -> User:
    user = User(
        id=user_dict['id'],
        name=user_dict['displayName'],
        username=user_dict['username'],
        bio=user_dict['bio'],
    )
    return user


def parse_user_preview(user_dict: ApiData) -> UserPreview:
    user_preview = UserPreview(
        id=user_dict['id'],
        name=user_dict['displayName'],
    )
    return user_preview


def parse_room(room_dict: ApiData) -> Room:
    room = Room(
        id=room_dict['id'],
        creator_id=room_dict.get('creatorId'),
        name=room_dict['name'],
        description=room_dict['description'],
        is_private=room_dict['isPrivate'],
        users={}
    )
    return room


def parse_room_preview(room_dict: ApiData) -> RoomPreview:
    user_previews = room_dict.get('peoplePreviewList', [])
    room_preview = RoomPreview(
        id=room_dict['id'],
        creator_id=room_dict['creatorId'],
        name=room_dict['name'],
        description=room_dict['description'],
        is_private=room_dict['isPrivate'],
        users={user['id']: parse_user_preview(user) for user in user_previews}
    )
    return room_preview

############################# Event Parsers ############################


def parse_auth(doge: 'DogeClient', data: ApiData) -> ReadyEvent:
    user_dict = data.get('p')
    if user_dict is None or not isinstance(user_dict, dict):
        # TODO: improve error messages here, e.g. for empty/wrong tokens
        raise TypeError(f"Bad response for user: {data}")

    user = parse_user(user_dict)
    doge.user = user
    return ReadyEvent(user=user)


def parse_rooms_fetched(doge: 'DogeClient', data: ApiData) -> RoomsFetchedEvent:
    data_dict = data.get('p')
    if data_dict is None or not isinstance(data_dict, dict):
        raise TypeError(f"Bad response for top rooms: {data}")

    rooms_data = data_dict['rooms']
    rooms = [parse_room_preview(room) for room in rooms_data]
    doge.top_rooms = rooms
    return RoomsFetchedEvent(rooms=rooms)


def parse_room_joined(doge: 'DogeClient', data: ApiData) -> RoomJoinEvent:
    room_dict = data.get('p')
    if room_dict is None or not isinstance(room_dict, dict):
        raise TypeError(f"Bad response for room: {data}")

    doge.room = parse_room(room_dict)

    assert doge.user is not None
    doge.room.users[doge.user.id] = doge.user

    return RoomJoinEvent(
        room=doge.room,
        as_speaker=True,
    )


def parse_user_joined(doge: 'DogeClient', data: ApiData) -> UserJoinEvent:
    data_dict = data.get('d', {})
    user_dict = data_dict.get('user')
    user = parse_user(user_dict)

    assert doge.room is not None
    doge.room.users[user.id] = user

    return UserJoinEvent(user)


def parse_user_left(doge: 'DogeClient', data: ApiData) -> UserLeaveEvent:
    data_dict = data.get('d', {})
    if data_dict is None or not isinstance(data_dict, dict):
        raise TypeError(f"Bad response for userid: {data}")

    left_user_id = data_dict['userId']

    assert doge.room is not None
    left_user = doge.room.users[left_user_id]

    del doge.room.users[left_user_id]

    return UserLeaveEvent(
        room_id=data_dict['roomId'],
        user=left_user
    )


def parse_message_event(doge: 'DogeClient', data: ApiData) -> MessageEvent:
    msg_dict = data.get('p')
    if msg_dict is None or not isinstance(msg_dict, dict):
        raise TypeError(f"Bad response for message: {data}")

    author_id = msg_dict['from']
    assert doge.room is not None
    author = doge.room.users[author_id]

    msg = Message(
        id=msg_dict['id'],
        author=author,
        content=parse_tokens_to_message(msg_dict['tokens']),
        is_whisper=msg_dict['isWhisper'],
    )
    return MessageEvent(msg)


def parse_message_deleted_event(doge: 'DogeClient', data: ApiData) -> MessageDeleteEvent:
    msg_dict = data.get('p')
    if msg_dict is None or not isinstance(msg_dict, dict):
        raise TypeError(f'Bad response for message: {data}')

    return MessageDeleteEvent(
        message_id=msg_dict['messageId'],
        author_id=msg_dict['userId'],
        deleter_id=msg_dict['deleterId']
    )


def parse_chat_member(doge: 'DogeClient', data: ApiData) -> ChatMemberEvent:
    msg_dict = data.get('d')
    if msg_dict is None or not isinstance(msg_dict, dict):
        raise TypeError(f'Bad response for chat member: {data}')

    chat_member = ChatMember(msg_dict['userId'])

    return ChatMemberEvent(chat_member=chat_member)


def parse_room_member(doge: 'DogeClient', data: ApiData) -> RoomMemberEvent:
    msg_dict = data.get('d')
    if msg_dict is None or not isinstance(msg_dict, dict):
        raise ValueError(f'Bad response for room member: {data}')

    room_member = RoomMember(msg_dict['userId'])

    return RoomMemberEvent(room_member=room_member)


def parse_room_banned_users_fetched(doge: 'DogeClient', data: ApiData) -> FetchRoomBannedUsersEvent:
    data_dict = data.get('p')
    if data_dict is None or not isinstance(data_dict, dict):
        raise ValueError(f'Bad response for banned room users: {data}')

    banned_users_data = data_dict['users']
    banned_users = [parse_user(user_dict) for user_dict in banned_users_data]
    return FetchRoomBannedUsersEvent(banned_users)


def parse_muted_event(doge: 'DogeClient', data: ApiData) -> StateEvent:
    doge.is_muted = not doge.is_muted
    return StateEvent(doge.is_muted)


def parse_deafened_event(doge: 'DogeClient', data: ApiData) -> StateEvent:
    doge.is_deafened = not doge.is_deafened
    return StateEvent(doge.is_deafened)


def parse_hand_raised_event(doge: 'DogeClient', data: ApiData) -> HandRaisedEvent:
    msg_dict = data.get('d')
    if msg_dict is None or not isinstance(msg_dict, dict):
        raise ValueError(f'Bad response for hand raised: {data}')

    return HandRaisedEvent(msg_dict['userId'])


def parse_command_execute_event(doge: 'DogeClient', event: MessageEvent) -> CommandEvent: # Todo make a parse_comamnd_event parser to use in init _run_command and here
    msg = event.message

    try:
        command_name, content = msg.content.split(' ', 1)
        if len(content.strip()) == 0:
            raise ValueError
    except ValueError:
        command_name, content = msg.content.strip(), ''

    arguments = []
    if content:
        for arg in content.split(' ', 99):  # max_split + 1 max args
            if len(arg.strip()) > 0:
                arguments.append(arg.strip())
        else:
            arguments = []

    return CommandEvent(
        message=msg,
        command_name=command_name,
        arguments=arguments
    )
