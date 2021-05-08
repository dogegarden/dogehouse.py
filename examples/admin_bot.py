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
async def mute(event: CommandEvent) -> None:
    """You can add an owner check here if you want:
    if event.message.author.id == owner_id:
        await doge.toggle_mute()
    """
    await doge.set_mute(not doge.is_muted)


@doge.command
async def deafen(event: CommandEvent) -> None:
    await doge.set_deafen(not doge.is_deafened)


@doge.on_mute_change
async def toggle_mute(event: StateEvent) -> None:
    await doge.send_message(f'I\'ve changed my mute state to: {event.state}')


@doge.on_deafen_change
async def toggle_deafen(event: StateEvent) -> None:
    await doge.send_message(f'I\'ve changed my deafen state to: {event.state}')

doge.run()
