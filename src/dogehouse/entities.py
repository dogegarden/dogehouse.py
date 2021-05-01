from typing import Any, Awaitable, Callable, Dict, NamedTuple, Optional, TypeVar

ApiData = Dict[str, Any]

T = TypeVar('T')
Callback = Callable[[T], Awaitable[None]]


class UserPreview(NamedTuple):
    id: str
    name: str


class User(NamedTuple):
    id: str
    name: str
    username: str
    bio: str


class RoomPreview(NamedTuple):
    id: str
    creator_id: str
    name: str
    description: str
    is_private: bool
    users: Dict[str, UserPreview]


class Room(NamedTuple):
    id: str
    creator_id: Optional[str]
    name: str
    description: str
    is_private: bool
    users: Dict[str, User]


class Message(NamedTuple):
    id: str
    author: User
    content: str
    is_whisper: bool
