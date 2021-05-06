import json
import re
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


TOKENIZE_REGEX = re.compile(r"( |`.*?`)")


def tokenize_message(message: str) -> List[Dict[str, str]]:
    return [tokenize(string)
            for string in TOKENIZE_REGEX.split(message)
            if string.strip()]


def tokenize(string: str) -> Dict[str, str]:
    type = "text"

    if string.startswith("@") and len(string) > 2:
        type = "mention"
        string = string[1:]

    elif re.fullmatch(r"http[s]:\/\/.+", string, flags=re.IGNORECASE):
        type = "link"

    elif string.startswith(":") and string.endswith(":") and len(string) > 2:
        type = "emote"
        string = string[1:-1]

    elif string.startswith("`") and string.endswith("`") and len(string) > 2:
        type = "block"
        string = string[1:-1]

    return dict(t=type, v=string)
