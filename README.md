# dogehouse.py

Python wrapper for the dogehouse API.

[![pypi](https://img.shields.io/badge/pypi-dogehouse-blue)](https://pypi.org/project/dogehouse)

## Documentation

You can find the documentation at [The DogeGarden Wiki](https://wiki.dogegarden.net)

## Installation

`pip install dogehouse`

## Example

```python
from dogehouse import DogeClient
from dogehouse.entities import ReadyEvent, RoomJoinEvent, UserJoinEvent

doge = DogeClient("token", "refresh_token")

@doge.on_ready
async def make_my_room(event: ReadyEvent) -> None:
    print(f"Successfully connected as @{event.user.username}!")
    await doge.create_room("Hello World!")

@doge.on_user_join
async def greet_user(event: UserJoinEvent) -> None:
    await doge.send_message(f"Hello @{event.user.username}")

doge.run()
```

## Tokens

- Go to [dogehouse.tv](https://dogehouse.tv)
- Open Developer options (<kbd>F12</kbd> or <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>I</kbd>)
- Go to Application > Local Storage > dogehouse&period;tv
- There lies your `TOKEN` and `REFRESH_TOKEN`
