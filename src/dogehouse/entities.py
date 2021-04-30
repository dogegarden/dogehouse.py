from typing import Any, Awaitable, Callable, Dict, NamedTuple, TypeVar, Union

ApiData = Dict[str, Any]

T = TypeVar('T')
Callback = Callable[[T], Awaitable[None]]


class RawEvent(NamedTuple):
    opcode: str
    data: Dict[str, str]


class User(NamedTuple):
    id: str
    name: str
    username: str
    bio: str


class Room(NamedTuple):
    id: str
    creator_id: str
    name: str
    description: str
    is_private: bool
    users: Dict[str, User]


class Message(NamedTuple):
    id: str
    author: User
    content: str
    is_whisper: bool


class ReadyEvent(NamedTuple):
    user: User


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


Event = Union[
    ReadyEvent,
    RoomJoinEvent,
    UserJoinEvent,
    UserLeaveEvent,
    MessageEvent,
]
