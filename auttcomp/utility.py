import json
from types import SimpleNamespace
from typing import Iterable

def normalize(obj):
  if isinstance(obj, dict): return SimpleNamespace(**obj)
  return obj

class JsonUtil:
  @staticmethod
  def toObject(jsonStr):
    return json.loads(jsonStr, object_hook=lambda d: SimpleNamespace(**d))

class ObjUtil:

  @staticmethod
  def execGenerator(gen):
    if isinstance(gen, Iterable):
      return list(gen)
    else: return gen
