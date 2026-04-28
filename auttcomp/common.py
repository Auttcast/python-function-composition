from typing import Any, NamedTuple

def id_param(x:Any) -> Any:
    return x

KeyValuePair = NamedTuple('KeyValuePair', [('key', Any), ('value', Any)])
