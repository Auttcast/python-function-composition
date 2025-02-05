import sys
from types import SimpleNamespace
from typing import Iterable
from .quicklog import log, ConsoleColor

#explicite only
iterableTypes = [set, list]

def isListType(obj):
  if not isinstance(obj, Iterable): return False
  return any(list(map(lambda x: isinstance(obj, x), iterableTypes)))

def normalize(obj):
  if isListType(obj): return obj
  if isinstance(obj, SimpleNamespace): return obj
  if isinstance(obj, dict): return SimpleNamespace(**obj)
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
    if isinstance(self.d, dict):
      if name in super().getKeys():
        return self.d[name]
      return None
    elif isinstance(self.d, SimpleNamespace):
      return getattr(self.d, name)

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

class ObjUtil():

  @staticmethod
  def printProps(obj):
    print(f"\n")
    print(type(obj))
    if isinstance(obj, dict):
      for key in obj.keys():
        print(f"{ConsoleColor.HEADER}{key}{ConsoleColor.END}:: {obj[key]}")
    else:
      for attr in list(filter(lambda x: "__" not in x, dir(obj))):
        print(f"{ConsoleColor.HEADER}{attr}{ConsoleColor.END}: {getattr(obj, attr)}")

    print(f"\n")

class SysUtil():

  @staticmethod
  def getCallArgs(frame, withData=False):
    c = frame.f_code
    if withData:
      return SimpleNamespace(**{x: frame.f_locals[x] for x in c.co_varnames[:c.co_argcount]})
    else:
      return SimpleNamespace(**{x: type(frame.f_locals[x]) for x in c.co_varnames[:c.co_argcount]})

  @staticmethod
  def getCallDetail(frame, withData=False):
    file = frame.f_globals['__file__'] if '__file__' in frame.f_globals.keys() else ""
    if file is None: file = ""
    return SimpleNamespace(**{
      "meta": SimpleNamespace(**{"frame": frame, "file": file}),
      "func": frame.f_code.co_name,
      "args": SysUtil.getCallArgs(frame, withData)
    })

  @staticmethod
  def __enabled(withData, filterFunc, mapFunc):
    if mapFunc is None: mapFunc = lambda x: x
    def __partialEnable(frame, a, b):
      cd = SysUtil.getCallDetail(frame, withData)
      if filterFunc is not None:
        if filterFunc(cd):
          print(mapFunc(cd))
      else:
        print(mapFunc(cd))
    return __partialEnable

  @staticmethod
  def __disable(frame, a, b): pass

  @staticmethod
  def enableTracing(withData=False, filterFunc=None, mapFunc=None): # maskFunc callDetail -> bool
    sys.settrace(SysUtil.__enabled(withData, filterFunc, mapFunc))

  @staticmethod
  def disableTracing():
    sys.settrace(SysUtil.__disable)

