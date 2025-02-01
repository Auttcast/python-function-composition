from typing import Callable, Optional
import inspect
from .quicklog import log

enableLogging = False

class Composable:

  def __init__(self, func):
    self.isData = not isinstance(func, Callable)
    self.f = func
    self.g = None
    self.chained = False

  def __log(self, message):
    if enableLogging:
      log(f"DEBUG {self.__hash__()} {message}")

  def __isChained(self, target) -> Optional[bool]:
    if target is None: return None
    if not isinstance(target, Composable): return None
    return target.chained

  def __invokeNative(self, func, name, args):
    self.__log(f"START FUNCTION ----------------- {args} isData: {self.isData}")
    if self.isData: return (self.f,)
    r = func(*args)
    if type(r) not in [type((1,)), type(None)]: r = (r,)
    self.__log(f"END FUNCTION   ----------------- {args} ->  isData: {self.isData} r: {r}")
    return r
  
  def __invokeCompose(self, func, name, args):
    r = func(*args) if args is not None else func()
    return r
  
  def __internal_call(self, args):
    #self.__log(f"START __internal_call ----------------- {args} isData: {self.isData}")
    invokeF = self.__invokeCompose if isinstance(self.f, Composable) else self.__invokeNative
    result = invokeF(self.f, "f", args)
    
    if self.g is not None:
      invokeG = self.__invokeCompose if isinstance(self.g, Composable) else self.__invokeNative
      result = invokeG(self.g, "g", result)

    #self.__log(f"END __internal_call ----------------- {args} isData: {self.isData}")
    return result
    
  def __getChainState(self):
      terminatingUnchained = not self.chained and self.__isChained(self.f) == None and self.__isChained(self.g) == None
      terminatingChain = not self.chained and self.__isChained(self.g)
      return (terminatingUnchained, terminatingChain)
    
  def __call__(self, *args):
    try:
      r = self.__internal_call(args)
      (terminatingUnchained, terminatingChain) = self.__getChainState()
      isSingleTuple = type(r) == type((1,)) and len(r) == 1
      shouldUnpackResult = (terminatingChain or terminatingUnchained) and isSingleTuple
      
      if shouldUnpackResult:
        r = r[0]

      return r
    except Exception as inst:
      self.__log(f"EXCEPTION -------- {type(inst)} {inst} ARGS {args}")
      raise inst

  @staticmethod
  def __internalFactory(func): return Composable(func)

  #composition    
  def __or__(self, other):
    self.__log(f"__or__::: self {type(self)} other {type(other)}")
    
    if not isinstance(other, Composable): other = Composable.__internalFactory(other)

    newComp = Composable.__internalFactory(self)
    newComp.isData = self.isData
    self.chained = True
    newComp.chained = False
    otherComp = Composable.__internalFactory(other.f)
    otherComp.chained = True
    otherComp.isData = self.isData
    newComp.g = otherComp

    return newComp

  def __getParamCount(self, func):
    if isinstance(func, Composable): return self.__getParamCount(func.f)
    finsp = func
    if inspect.isclass(func): finsp = func.__call__
    return len(inspect.signature(finsp).parameters)
    
  def __curry_inline(self, fleft, fright, argCount):
    match argCount:
      case 2: return Composable.__internalFactory(lambda x: fleft(fright, x))
      case 3: return Composable.__internalFactory(lambda x1, x2: fleft(fright, x1, x2))
      case 4: return Composable.__internalFactory(lambda x1, x2, x3: fleft(fright, x1, x2, x3))
      case 5: return Composable.__internalFactory(lambda x1, x2, x3, x4: fleft(fright, x1, x2, x3, x4))
      case 6: return Composable.__internalFactory(lambda x1, x2, x3, x4, x5: fleft(fright, x1, x2, x3, x4, x5))
      case 7: return Composable.__internalFactory(lambda x1, x2, x3, x4, x5, x6: fleft(fright, x1, x2, x3, x4, x5, x6))
      case 8: return Composable.__internalFactory(lambda x1, x2, x3, x4, x5, x6, x7: fleft(fright, x1, x2, x3, x4, x5, x6, x7))
      case _: raise f"unsupported argument count {argCount}"
        
  #partial application
  def __and__(self, other):
    selfArgCount = self.__getParamCount(self)
    assumeNested = selfArgCount == 1
    
    if assumeNested: 
      return Composable.__internalFactory(lambda x: self(other)(x))
    return self.__curry_inline(self, other, selfArgCount)

  def __lt__(self, other):
    data = other.f
    nextFunc = self
    result = nextFunc(data)
    if isinstance(result, tuple) and len(result) == 1:
      result = result[0]
    return result
