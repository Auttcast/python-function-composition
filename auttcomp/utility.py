import sys
from types import SimpleNamespace
from .quicklog import log

#explicite only
iterableTypes = [set, list]

def isListType(obj):
  return any(list(map(lambda x: isinstance(obj, x), iterableTypes)))

def normalize(obj):
  if isListType(obj): return obj
  if isinstance(obj, dict) or isinstance(obj, SimpleNamespace): return DictWrapper(obj)
  log(f"WARNING normalize unexpected type {type(obj)}")
  return obj

def normalizeForKeyExists(obj):
  if isListType(obj): return obj
  if isinstance(obj, dict) or isinstance(obj, SimpleNamespace): return KeyExistWrapper(obj)
  log(f"WARNING normalizeForKeyExists unexpected type {type(obj)}")
  return obj

class BaseDictWrapper(dict):
  def __init__(self, d):
    super().__init__()
    self.d = d if not isinstance(d, SimpleNamespace) else vars(d)

  def getKeys(self):
    return self.d.keys()

class DictWrapper(BaseDictWrapper):
  def __init__(self, d):
    super().__init__(d)

  def __getattr__(self, name):
    if name in super().getKeys():
      return self.d[name]
    return None

class KeyExistWrapper(BaseDictWrapper):

  def __init__(self, d):
    super().__init__(d)

  def __getattr__(self, name):
    return name in super().getKeys()

def unwrapFromSingleTuple(obj):
  if isinstance(obj, tuple) and len(obj) == 1:
    return obj[0]
  return obj

def traceFrame(func):

  def enable(frame, a, b):
    log(SysUtil.getCallDetail(frame))

  def disable(frame, a, b): pass

  def traceFrameWrapper(*args, **kargs):
    sys.settrace(enable)
    try:
      return func(*args, **kargs)
    finally:
      sys.settrace(disable)
  return traceFrameWrapper

class SysUtil():

  @staticmethod
  def getCallArgs(frame):
    c = frame.f_code
    return {x: frame.f_locals[x] for x in c.co_varnames[:c.co_argcount]}

  @staticmethod
  def getCallDetail(frame):
    return {
      "func": frame.f_code.co_name,
      "args": SysUtil.getCallArgs(frame)
    }
