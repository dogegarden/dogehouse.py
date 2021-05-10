<p align="center">
  <img src="https://cdn.discordapp.com/attachments/820450983892222022/820961073980899328/dogegarden-bottom-cropped.png" alt="DogeGarden logo" />
</p>
<p align="center">
  <strong>A Python wrapper for DogeHouse 🐍</strong>
</p>
<p align="center">
  <a href="https://discord.gg/Nu6KVjJYj6">
    <img src="https://img.shields.io/discord/820442045264691201?style=for-the-badge" alt="discord - users online" />
  </a>
  <a href="https://pypi.org/project/dogehouse">
    <img src="https://img.shields.io/badge/pypi-dogehouse-blue?style=for-the-badge">
  </a>  
</p>

<h3 align="center">
  <a href="https://dogegarden.net">Website</a>
  <span> · </span>  
  <a href="https://stats.dogegarden.net">Tracker</a>
  <span> · </span>
  <a href="https://discord.gg/Nu6KVjJYj6">Discord</a>
  <span> · </span>
  <a href="https://wiki.dogegarden.net">Documentation</a>
</h3>

---

## Installation   <a href="https://pypi.org/project/dogehouse"><img src="https://img.shields.io/badge/pypi-dogehouse-blue"></a>  

`pip install dogehouse`

## Example

```python
from dogehouse import DogeClient
from dogehouse.events import ReadyEvent, UserJoinEvent, MessageEvent

doge = DogeClient("token", "refresh_token")


@doge.on_ready
async def make_my_room(event: ReadyEvent) -> None:
    print(f"Successfully connected as @{event.user.username}!")
    await doge.create_room("Hello dogehouse.py!")


@doge.on_user_join
async def greet_user(event: UserJoinEvent) -> None:
    await doge.send_message(f"Hello @{event.user.username}")


@doge.command
async def echo(event: MessageEvent) -> None:
    msg = event.message
    await doge.send_message(f'@{msg.author.username} said {msg.content}')


doge.run()
```

Check [examples](./examples/basic_bot.py) for more feature usage.

## Tokens

- Go to [dogehouse.tv](https://dogehouse.tv)
- Open Developer options (<kbd>F12</kbd> or <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>I</kbd>)
- Go to Application > Local Storage > dogehouse&period;tv
- There lies your `TOKEN` and `REFRESH_TOKEN`
