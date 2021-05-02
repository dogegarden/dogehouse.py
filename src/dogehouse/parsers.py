from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DogeClient

from .entities import ApiData, Message, Room, RoomPreview, User, UserPreview
from .events import (
    ReadyEvent, MessageEvent,
    RoomsFetchedEvent, RoomJoinEvent,
    UserJoinEvent, UserLeaveEvent,
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
