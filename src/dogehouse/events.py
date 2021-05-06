from typing import Awaitable, Callable, Dict, List, NamedTuple, TypeVar, Union

from .entities import Message, Room, RoomPreview, User


class RawEvent(NamedTuple):
    opcode: str
    data: Dict[str, str]


class ReadyEvent(NamedTuple):
    user: User


class RoomsFetchedEvent(NamedTuple):
    rooms: List[RoomPreview]


class RoomJoinEvent(NamedTuple):
    room: Room
    as_speaker: bool


class UserJoinEvent(NamedTuple):
    user: User


class UserLeaveEvent(NamedTuple):
    room_id: str
    user: User


class MessageEvent(NamedTuple):
    message: Message

class ChatUserEvent(NamedTuple):
    user_id: int

class ChatUserBannedEvent(ChatUserEvent):
    pass

class ChatUserUnbannedEvent(ChatUserEvent):
    pass

Event = Union[
    ReadyEvent,
    RoomsFetchedEvent,
    RoomJoinEvent,
    UserJoinEvent,
    UserLeaveEvent,
    MessageEvent,
    ChatUserEvent,
    ChatUserBannedEvent,
    ChatUserUnbannedEvent,
]
EventType = TypeVar(
    'EventType',
    ReadyEvent,
    RoomsFetchedEvent,
    RoomJoinEvent,
    UserJoinEvent,
    UserLeaveEvent,
    MessageEvent,
    ChatUserEvent,
    ChatUserBannedEvent,
    ChatUserUnbannedEvent,
)
Callback = Callable[[EventType], Awaitable[None]]
