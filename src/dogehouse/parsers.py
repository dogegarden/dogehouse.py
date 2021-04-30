import typing
from dogehouse.util import parse_tokens_to_message
from .entities import ApiData, Message, MessageEvent, Room, RoomJoinEvent, User

if typing.TYPE_CHECKING:
    from dogehouse import DogeClient


def parse_user(data: ApiData) -> User:
    user_dict = data.get('p')
    if user_dict is None or not isinstance(user_dict, dict):
        raise TypeError(f"Bad response for user: {data}")

    user = User(
        id=user_dict['id'],
        name=user_dict['displayName'],
        username=user_dict['username'],
        bio=user_dict['bio'],
    )
    return user


def parse_room_created(doge: 'DogeClient', data: ApiData) -> RoomJoinEvent:
    room_id_dict = data.get('d')
    if room_id_dict is None or not isinstance(room_id_dict, dict):
        raise TypeError(f"Bad response for room-created: {data}")

    room_id = str(room_id_dict['roomId'])

    assert doge.room is not None
    assert doge.room.id == room_id
    return RoomJoinEvent(
        room=doge.room,
        as_speaker=True,
    )


def parse_room(data: ApiData) -> Room:
    room_dict = data.get('p')
    if room_dict is None or not isinstance(room_dict, dict):
        raise TypeError(f"Bad response for room: {data}")

    room = Room(
        id=room_dict['id'],
        creator_id=room_dict['creatorId'],
        name=room_dict['name'],
        description=room_dict['description'],
        is_private=room_dict['isPrivate'],
    )
    return room


def parse_message_event(doge: 'DogeClient', data: ApiData) -> MessageEvent:
    msg_dict = data.get('p')
    if msg_dict is None or not isinstance(msg_dict, dict):
        raise TypeError(f"Bad response for message: {data}")

    msg = Message(
        id=msg_dict['id'],
        # author=parse_user(msg_dict['user']),
        author=msg_dict['from'],
        content=parse_tokens_to_message(msg_dict['tokens']),
        is_whisper=msg_dict['isWhisper'],
    )
    return MessageEvent(msg)
