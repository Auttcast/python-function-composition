from typing import Any, NamedTuple

def id_param(x:Any) -> Any:
    return x

class KeyValuePair[K, V](NamedTuple):
    key:K
    value:V
