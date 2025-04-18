from collections import namedtuple
from typing import Any

def id_param(x:Any) -> Any:
    return x

KeyValuePair = namedtuple("KeyValuePair", ["key", "value"])
