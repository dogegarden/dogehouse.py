import os

from dogehouse import DogeClient
from dogehouse.events import *

#owner_id = 'your_id_here'

token = os.getenv('TOKEN', '')
refresh_token = os.getenv('REFRESH_TOKEN', '')

doge = DogeClient(token, refresh_token)

@doge.on_ready
async def ready(event: ReadyEvent) -> None:
    await doge.create_room('Admin-bot')

@doge.command
async def mute(event: MessageEvent) -> None:
    """You can add an owner check here if you want:
    if event.message.author.id == owner_id:
        await doge.toggle_mute()
    """
    await doge.toggle_mute()

@doge.command
async def deafen(event: MessageEvent) -> None:
    await doge.toggle_deafen()

@doge.on_mute_change
async def mute_change(event: StateEvent) -> None:
    await doge.send_message(f'I\'ve changed my mute state to: {event.state}')

@doge.on_deafen_change
async def deafen_change(event: StateEvent) -> None:
    await doge.send_message(f'I\'ve changed my deafen state to: {event.state}')

doge.run()