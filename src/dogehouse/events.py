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

class MessageDeleteEvent(NamedTuple):
    message_id: int
    author_id: int
    deleter_id: int


Event = Union[
    ReadyEvent,
    RoomsFetchedEvent,
    RoomJoinEvent,
    UserJoinEvent,
    UserLeaveEvent,
    MessageEvent,
    MessageDeleteEvent,
]
EventType = TypeVar(
    'EventType',
    ReadyEvent,
    RoomsFetchedEvent,
    RoomJoinEvent,
    UserJoinEvent,
    UserLeaveEvent,
    MessageEvent,
    MessageDeleteEvent,
)
Callback = Callable[[EventType], Awaitable[None]]
