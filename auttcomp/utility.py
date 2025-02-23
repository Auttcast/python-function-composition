import json
from types import SimpleNamespace
from typing import Iterable

class JsonUtil:
  @staticmethod
  def to_object(json_str):
    return json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))

class ObjUtil:

  @staticmethod
  def exec_generator(gen):
    if isinstance(gen, dict):
      #note dict is iterable
      return gen
    if isinstance(gen, Iterable):
      return list(gen)
    else: return gen
