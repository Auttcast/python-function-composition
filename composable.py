from typing import Callable, Optional
from collections.abc import Iterable

#RULES:
#Composer has two objectives
#1: wrap lambdas in composable functionality: f
#2: optionally contain another composed function: g

#g will only exist if Composable was created from a chain

class Composable:

  def __init__(self, func: Callable):
    self.f = func
    self.g = None
    self.chained = False
    self.name = "f"
    
  def log(self, message):
    if True:
      print(f"DEBUG {self.__hash__()} {message}")
    
  def __isComposable(self, target): return type(target) == type(self)
    
  def isChained(self, target) -> Optional[bool]:
    if target is None: return None
    if not self.__isComposable(target): return None
    return target.chained
    
#rules:
#single-param functions require args to pass as shape (1,)
#multi-param functions require unpacking
  def __invokeNative(self, func, name, args):
    self.log(f"START FUNCTION -----------------{name} {args}")
    
    r = func(*args)
    if type(r) is not type((1,)): r = (r,)
    
    self.log(f"START FUNCTION -----------------{name} {args} -> {r}")
    return r
  
  def __invokeCompose(self, func, name, args):
    self.log(f"START COMPOSE -----------------{name} {args}")
    r = func(*args)
    self.log(f"END COMPOSE -----------------{name} {args} -> {r}")
    return r
  
  def _internal_call(self, args):
  
    invokeF = self.__invokeCompose if self.__isComposable(self.f) else self.__invokeNative
    result = invokeF(self.f, "f", args)
    
    if self.g is not None:
      invokeG = self.__invokeCompose if self.__isComposable(self.g) else self.__invokeNative
      result = invokeG(self.g, "g", result)
      
    return result
    
  def __getChainState(self):
      terminatingUnchained = not self.chained and self.isChained(self.f) == None and self.isChained(self.g) == None
      terminatingChain = not self.chained and self.isChained(self.g)
      return (terminatingUnchained, terminatingChain)
    
  def __call__(self, *args):
    #self.log(f"------------------------------------ __call__ start")
    try:
    
      r = self._internal_call(args)
 
      self.log(f"CHAIN {self.name} self: {self.chained} g: {self.isChained(self.g)} f: {self.isChained(self.f)}")
      
      (terminatingUnchained, terminatingChain) = self.__getChainState()
      
      self.log(f"END UNCHAINED {self.name}") if terminatingUnchained else None
      self.log(f"END CHAINED") if terminatingChain else None
      
      isSingleTuple = type(r) == type((1,)) and len(r) == 1
      shouldUnpackResult = (terminatingChain or terminatingUnchained) and isSingleTuple
      
      if (shouldUnpackResult):
        r = r[0]
        self.log(f"UNPACKEDDD end ------------------------------------ RETURNS {r}")
      
      self.log(f"__call__ end ------------------------------------  RETURNS {r}")
      return r
    except Exception as inst:
      self.log(f"EXCEPTION -------- {type(inst)} {inst}")
      raise inst
      
  def __or__(self, other):
    if self.__isComposable(other):
        newComp = Composable(self)
        self.chained = True
        newComp.chained = False
        newComp.name = f"{self.name}+"
        otherComp = Composable(other.f)
        otherComp.chained = True
        newComp.g = otherComp
        return newComp
    else:
        raise TypeError(f"Unsupported operand type(s) for |: 'Composable' and '{type(other).__name__}'")

