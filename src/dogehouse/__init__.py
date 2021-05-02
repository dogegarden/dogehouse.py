import asyncio
import functools
import json
import logging
from logging import info
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

import websockets
from websockets import WebSocketClientProtocol
from websockets.exceptions import WebSocketException

from .entities import ApiData, Room, RoomPreview, User, Message, UserPreview
from .events import (
    Callback, Event, ReadyEvent, MessageEvent,
    RoomsFetchedEvent, RoomJoinEvent,
    UserJoinEvent, UserLeaveEvent,
)
from .constants import (
    GET_TOP_ROOMS, JOIN_ROOM, READY, MESSAGE,
    CREATE_ROOM, ROOMS_FETCHED, ROOM_CREATED, ROOM_JOINED, USER_JOINED, USER_LEFT,
    SEND_MESSAGE,
)
from .parsers import (
    parse_auth, parse_message_event,
    parse_room_joined, parse_rooms_fetched,
    parse_user_joined, parse_user_left,
)
from .util import format_response, tokenize_message

api_url = "wss://api.dogehouse.tv/socket"
api_version = "0.2.0"


class DogeClient:
    def __init__(self, token: str, refresh_token: str, prefix: str = '.') -> None:
        self.token = token
        self.refresh_token = refresh_token
        self.prefix = prefix

        self._socket: Optional[WebSocketClientProtocol] = None
        self.loop = asyncio.get_event_loop()

        self.user: Optional[User] = None
        self.room: Optional[Room] = None
        self.top_rooms: List[RoomPreview] = []

        self.event_hooks: Dict[str, Callback[Any]] = {}
        self._commands: Dict[str, Callback[MessageEvent]] = {}

    ########################## Client Methods ##########################

    async def create_room(
            self,
            name: str,
            description: str = "",
            public: bool = True
    ) -> None:
        if not 2 <= len(name) <= 60:
            raise ValueError(
                "Room name should be between 2 and 60 characters long"
            )

        await self._send(
            CREATE_ROOM,
            name=name,
            description=description,
            privacy="public" if public else "private",
        )

    async def join_room(self, room: RoomPreview) -> None:
        await self._send(JOIN_ROOM, roomId=room.id, creatorId=room.creator_id)

    async def send_message(self, message: str, *, whisper_to: List[UserPreview] = []) -> None:
        if not self.room:
            raise RuntimeError("No room has been joined yet!")

        await self._send(
            SEND_MESSAGE,
            whisperedTo=[user.id for user in whisper_to],
            tokens=tokenize_message(message)
        )

    ############################## Events ##############################

    event_parsers: Dict[str, Callable[['DogeClient', ApiData], Event]] = {
        ROOM_CREATED: parse_room_joined,
        ROOM_JOINED: parse_room_joined,
        ROOMS_FETCHED: parse_rooms_fetched,
        USER_JOINED: parse_user_joined,
        USER_LEFT: parse_user_left,
        MESSAGE: parse_message_event,
    }

    async def new_event(self, data: ApiData) -> None:
        # TODO: error handling, data.get('e')
        event_name = data.get('op')
        if event_name not in self.event_parsers:
            return

        info(f'received event: {event_name}')

        if event_name == MESSAGE:
            msg_event = parse_message_event(self, data)
            if msg_event.message.content.startswith(self.prefix):
                await self._run_command(msg_event)

        callback = self.event_hooks.get(event_name)
        if callback is None:
            return

        parser = self.event_parsers[event_name]
        event = parser(self, data)
        await callback(event)

    def on_ready(self, callback: Callback[ReadyEvent]) -> Callback[ReadyEvent]:
        self.event_hooks[READY] = callback
        return callback

    def on_rooms_fetch(self, callback: Callback[RoomsFetchedEvent]) -> Callback[RoomsFetchedEvent]:
        self.event_hooks[ROOMS_FETCHED] = callback
        return callback

    def on_room_join(self, callback: Callback[RoomJoinEvent]) -> Callback[RoomJoinEvent]:
        self.event_hooks[ROOM_CREATED] = callback
        self.event_hooks[ROOM_JOINED] = callback
        return callback

    def on_user_join(self, callback: Callback[UserJoinEvent]) -> Callback[UserJoinEvent]:
        self.event_hooks[USER_JOINED] = callback
        return callback

    def on_user_leave(self, callback: Callback[UserLeaveEvent]) -> Callback[UserLeaveEvent]:
        self.event_hooks[USER_LEFT] = callback
        return callback

    def on_message(self, callback: Callback[MessageEvent]) -> Callback[MessageEvent]:
        @functools.wraps(callback)
        async def wrapped_callback(event: MessageEvent) -> None:
            if self.user is None:
                raise ValueError("Received message, but User is not set")

            if event.message.author.id == self.user.id:
                return

            await callback(event)

        self.event_hooks[MESSAGE] = wrapped_callback
        return wrapped_callback

    def command(self, callback: Callback[MessageEvent]) -> Callback[MessageEvent]:
        command_trigger = self.prefix + callback.__name__
        self._commands[command_trigger] = callback
        return callback

    async def _run_command(self, event: MessageEvent) -> None:
        text = event.message.content
        command_trigger, content = text.split(' ', 1)
        if command_trigger in self._commands:
            callback = self._commands[command_trigger]

            modified_event = MessageEvent(
                message=Message(
                    id=event.message.id,
                    author=event.message.author,
                    is_whisper=event.message.is_whisper,
                    content=content,
                )
            )
            await callback(modified_event)

    ######################### Internal methods #########################

    def run(self) -> None:
        try:
            self.loop.run_until_complete(self._start())
        except KeyboardInterrupt:
            pass
        finally:
            asyncio.ensure_future(self._disconnect())

    def _debug_on(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

    async def _send(self, opcode: str, **data: Any) -> str:
        if self._socket is None:
            raise WebSocketException("Socket not initialized")

        ref = str(uuid4())
        msg = dict(op=opcode, d=data,
                   reference=ref, version=api_version)

        await self._socket.send(json.dumps(msg))

        return ref

    async def _recv(self) -> websockets.Data:
        if self._socket is None:
            raise WebSocketException("Socket not initialized")

        while True:
            message = await self._socket.recv()
            if len(message) > 0:
                return message

    async def _start(self) -> None:
        await self._connect()
        await self._get_raw_events()

    async def _connect(self) -> None:
        self._socket = await websockets.connect(api_url)
        info("websocket connected")

        await self._send(
            'auth:request',
            accessToken=self.token,
            refreshToken=self.refresh_token,
            platform="dogehouse.py",
        )
        await self._authenticate()

    async def _authenticate(self) -> None:
        assert self._socket is not None
        auth_response = await self._recv()
        data = format_response(auth_response)
        ready_event = parse_auth(self, data)

        callback = self.event_hooks.get(READY)
        if callback is not None:
            await callback(ready_event)

        await self._send(GET_TOP_ROOMS)

    async def _get_raw_events(self) -> None:
        while self._socket is not None:
            response = await self._recv()
            data = format_response(response)
            await self.new_event(data)

    async def _disconnect(self) -> None:
        if self._socket is not None:
            await self._socket.close()
