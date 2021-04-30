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
    # users: List[Union[User, UserPreview]] # TODO


class Message(NamedTuple):
    id: str
    author: str  # TODO: pass User object here
    content: str
    is_whisper: bool


class ReadyEvent(NamedTuple):
    user: User


class RoomJoinEvent(NamedTuple):
    room: Room
    as_speaker: bool


class MessageEvent(NamedTuple):
    message: Message


Event = Union[ReadyEvent, RoomJoinEvent, MessageEvent]
