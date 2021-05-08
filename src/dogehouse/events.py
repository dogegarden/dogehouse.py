from typing import Awaitable, Callable, Dict, List, NamedTuple, TypeVar, Union

from .entities import Message, Room, RoomPreview, User, ChatMember, RoomMember


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


class CommandEvent(NamedTuple):
    message: Message
    command_name: str
    arguments: List[str]


class MessageDeleteEvent(NamedTuple):
    message_id: str
    author_id: str
    deleter_id: str


class ChatMemberEvent(NamedTuple):
    chat_member: ChatMember


class RoomMemberEvent(NamedTuple):
    room_member: RoomMember


class FetchRoomBannedUsersEvent(NamedTuple):
    banned_users: List[User]


class StateEvent(NamedTuple):
    state: bool


class HandRaisedEvent(NamedTuple):
    user_id: str


Event = Union[
    ReadyEvent,
    RoomsFetchedEvent,
    RoomJoinEvent,
    UserJoinEvent,
    UserLeaveEvent,
    MessageEvent,
    MessageDeleteEvent,
    ChatMemberEvent,
    RoomMemberEvent,
    FetchRoomBannedUsersEvent,
    StateEvent,
    HandRaisedEvent,
    CommandEvent,
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
    ChatMemberEvent,
    RoomMemberEvent,
    FetchRoomBannedUsersEvent,
    StateEvent,
    HandRaisedEvent,
    CommandEvent,
)
Callback = Callable[[EventType], Awaitable[None]]
