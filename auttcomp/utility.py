import json
from types import SimpleNamespace
from typing import Iterable

concreteIterableTypes = [set, list]

def isListType(obj):
  if not isinstance(obj, Iterable): return False
  return any(list(map(lambda x: isinstance(obj, x), concreteIterableTypes)))

def normalize(obj):
  if isListType(obj): return obj
  if isinstance(obj, SimpleNamespace): return obj
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
