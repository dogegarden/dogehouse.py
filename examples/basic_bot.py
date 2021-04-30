import logging

from dogehouse import DogeClient
from dogehouse.entities import (MessageEvent, ReadyEvent, RoomJoinEvent,
                                UserJoinEvent)

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYxOTc4MzQ5MywiaWF0IjoxNjE5Nzc5ODkzLCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwdDlxZXBiZ29zcDNmZ21hbzAxMjdsMSIsIm5iZiI6MTYxOTc3OTg5MywidXNlcklkIjoiZDA3NGUyYmMtYjY1MS00NDRmLTgyMGUtYjExMTRhNDZkNmU1In0.gTDf8jI-BL9IpNEQBJ6n2koz_aXPl4jXba9fgkGyH70"
refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYyMjM3MTg5MywiaWF0IjoxNjE5Nzc5ODkzLCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwdDlxZXBiaDQ5bjdmZ21hbzAxMjdtMSIsIm5iZiI6MTYxOTc3OTg5MywidG9rZW5WZXJzaW9uIjoxLCJ1c2VySWQiOiJkMDc0ZTJiYy1iNjUxLTQ0NGYtODIwZS1iMTExNGE0NmQ2ZTUifQ.31a8nOvfqaW3ZbEBbnGJ6nyaZbcBzXP2eRmpfDPZG1g"

doge = DogeClient(token, refresh_token)


@doge.on_ready
async def make_my_room(event: ReadyEvent) -> None:
    print(f"Successfully connected as @{event.user.username}!")
    await doge.create_room("Hello World!")


@doge.on_room_join
async def joined_room(event: RoomJoinEvent) -> None:
    print("Joined room", event.room.name)


@doge.on_user_join
async def greet_user(event: UserJoinEvent) -> None:
    await doge.send_message(f"Hello @{event.user.username}")


@doge.on_message
async def echo(event: MessageEvent) -> None:
    await doge.send_message(f'@{event.message.author} said {event.message.content}')


doge.run()
