import asyncio
import functools
import json
from logging import debug, info
from typing import Any, Callable, Dict, Optional
from uuid import uuid4

import websockets
from websockets import WebSocketClientProtocol
from websockets.exceptions import WebSocketException

from .entities import (
    ApiData, Callback,
    MessageEvent, ReadyEvent, RoomJoinEvent,
    Room,  User,
)
from .events import (
    ON_MESSAGE, ON_READY, ON_ROOM_JOIN,
    NEW_TOKENS, ROOM_CREATED,
    ROOM_CREATE, ROOM_CREATE_REPLY, SEND_MESSAGE,
)
from .parsers import parse_message_event, parse_room, parse_room_created, parse_user
from .util import format_response, tokenize_message

api_url = "wss://api.dogehouse.tv/socket"
api_version = "0.2.0"


class DogeClient:
    def __init__(self, token: str, refresh_token: str):
        self.token = token
        self.refresh_token = refresh_token

        self._socket: Optional[WebSocketClientProtocol] = None
        self.loop = asyncio.get_event_loop()

        self.user: Optional[User] = None
        self.room: Optional[Room] = None

        self.event_hooks: Dict[str, Callback[Any]] = {}

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
            ROOM_CREATE,
            name=name,
            description=description,
            privacy="public" if public else "private",
        )

        roomData = await self._wait_for(ROOM_CREATE_REPLY)
        self.room = parse_room(roomData)

    async def send_message(self, message: str) -> None:
        if not self.room:
            raise RuntimeError("No room has been joined yet!")

        await self._send(
            SEND_MESSAGE,
            whisperedTo=[],
            tokens=tokenize_message(message)
        )

    ############################## Events ##############################

    event_parsers: Dict[str, Callable[['DogeClient', ApiData], Any]] = {
        ROOM_CREATED: parse_room_created,
        ON_MESSAGE: parse_message_event,
        # YOU_JOINED_AS_SPEAKER: parse_room_voice,
    }

    async def new_event(self, data: ApiData) -> None:
        event_name = data.get('op')
        if event_name not in self.event_parsers:
            return

        info(f'received {event_name=}')

        parser = self.event_parsers[event_name]
        event = parser(self, data)

        await self.run_callback(event_name, event)

    async def run_callback(self, event_name: str, event: Any) -> None:
        callback = self.event_hooks.get(event_name)
        if callback is None:
            return

        await callback(event)

    def on_ready(self, callback: Callback[ReadyEvent]) -> Callback[ReadyEvent]:
        self.event_hooks[ON_READY] = callback
        return callback

    def on_room_join(self, callback: Callback[RoomJoinEvent]) -> Callback[RoomJoinEvent]:
        self.event_hooks[ROOM_CREATED] = callback
        return callback

    def on_message(self, callback: Callback[MessageEvent]) -> Callback[MessageEvent]:
        @functools.wraps(callback)
        async def wrapped_callback(event: MessageEvent) -> None:
            if self.user is None:
                raise ValueError("Received message, but User is not set")

            if event.message.author == self.user.id:
                return

            await callback(event)

        self.event_hooks[ON_MESSAGE] = wrapped_callback
        return callback

    ######################### Internal methods #########################

    def run(self) -> None:
        try:
            self.loop.run_until_complete(self._start())
        except KeyboardInterrupt:
            pass
        finally:
            asyncio.ensure_future(self._disconnect())

    async def _send(self, opcode: str, **data: Any) -> str:
        if self._socket is None:
            raise WebSocketException("Socket not initialized")

        ref = str(uuid4())
        msg = dict(op=opcode, d=data,
                   reference=ref, version=api_version)

        await self._socket.send(json.dumps(msg))

        return ref

    async def _wait_for(self, opcode: str) -> ApiData:
        if self._socket is None:
            raise WebSocketException("Socket not initialized")

        response = await self._socket.recv()
        data = format_response(response)
        if data.get('op') != opcode:
            raise ValueError(f"expected '{opcode}', got {data}")

        return data

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
        auth_response = await self._socket.recv()
        data = format_response(auth_response)
        self.user = parse_user(data)

        await self.run_callback(ON_READY, ReadyEvent(self.user))

    async def _get_raw_events(self) -> None:
        while self._socket is not None:
            response = await self._socket.recv()
            data = format_response(response)
            await self.new_event(data)

    async def _disconnect(self) -> None:
        if self._socket is not None:
            await self._socket.close()
