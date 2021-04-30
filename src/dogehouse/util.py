import json
from json.decoder import JSONDecodeError
from typing import Dict, List

import websockets

from .entities import ApiData


def format_response(response: websockets.Data) -> ApiData:
    if isinstance(response, bytes):
        message = response.decode()
    else:
        message = response

    try:
        data = json.loads(message)
    except JSONDecodeError:
        data = {}

    assert isinstance(data, dict)
    return data


def parse_tokens_to_message(tokens: List[Dict[str, str]]) -> str:
    """
    Parse a collection of tokens into a usable/readable string.

    Args:
        tokens (List[Dict[str, str]]): The message tokens that should be parsed.

    Returns:
        str: The parsed collection its content
    """
    return " ".join(map(parse_token_to_message, tokens))


message_formats = {
    "mention": "@{}",
    "emote": ":{}:",
    "block": "`{}`"
}


def parse_token_to_message(token: Dict[str, str]) -> str:
    type, value = token['t'], token['v']
    fmt = message_formats.get(type)
    if fmt is None:
        return value

    return fmt.format(value)


def tokenize_message(message: str) -> List[Dict[str, str]]:
    return [tokenize_word(word) for word in message.split()]


def tokenize_word(word: str) -> Dict[str, str]:
    """
    Convert a word into a dogehouse message token.

    Args:
        word (str): The word that should be parsed.

    Returns:
        Dict[str, str]: A token which represents the word.
    """
    # TODO: Do some regex magic instead of this
    t, v = "text", str(word)
    if v.startswith("@") and len(v) >= 3:
        t = "mention"
        v = v[1:]
    elif v.startswith("http") and len(v) >= 8:
        t = "link"
    elif v.startswith(":") and v.endswith(":") and len(v) >= 3:
        t = "emote"
        v = v[1:-1]
    elif v.startswith("`") and v.endswith("`") and len(v) >= 3:
        t = "block"
        v = v[1:-1]

    return dict(t=t, v=v)


# def parse_event(data: ApiData) -> Event:
#     # if data.get('d') is None:
#     #     raise TypeError(f"Bad response for event: {data}")

#     user_dict = data.get('p')
#     user = None if user_dict is None else parse_user(data)

#     event = Event(
#         id=data.get('id'),
#         type=data.get('op'),
#         message=data.get('msg'),
#         user=user,
#         room=data.get('room'),
#     )
#     return event
