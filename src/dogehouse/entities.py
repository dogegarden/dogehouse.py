from dataclasses import dataclass
from typing import Any, Dict, Optional

ApiData = Dict[str, Any]


@dataclass(frozen=True)
class UserPreview:
    id: str
    name: str


@dataclass(frozen=True)
class User(UserPreview):
    username: str
    bio: str


@dataclass(frozen=True)
class _RoomBase:
    id: str
    creator_id: Optional[str]
    name: str
    description: str
    is_private: bool


@dataclass(frozen=True)
class RoomPreview(_RoomBase):
    users: Dict[str, UserPreview]


@dataclass(frozen=True)
class Room(_RoomBase):
    users: Dict[str, User]


@dataclass(frozen=True)
class Message:
    id: str
    author: User
    content: str
    is_whisper: bool


@dataclass(frozen=True)
class ChatMember:
    id: str


@dataclass(frozen=True)
class RoomMember:  # TODO: Use it when fetching is implemented in on_room_user_banned
    id: str
