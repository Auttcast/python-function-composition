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
    
  def __getType(self, target):
    isComp = self.__isComposable(target)    
    funcType = f"compose-{target.name}" if isComp else "function"
    return funcType
    
  def __invoke(self, func, name, args):

    r = func(*args) 
    
    if not self.__isComposable(func):
      r = (r,)
    
    return r
  
  def _internal_call(self, args):
    fr = self.__invoke(self.f, "f", args)
    result = self.__invoke(self.g, "g", fr) if not self.g is None else fr  
    return result
    
  def __call__(self, *args):
    self.log(f"------------------------------------ __call__ start {self.__getType(self)}")
    try:
    
      r = self._internal_call(args)
      self.log(f"----------------- returning.... {r}")
 
      self.log(f"CHAIN {self.name} self: {self.chained} g: {self.isChained(self.g)} f: {self.isChained(self.f)}")
      
      terminatingUnchained = not self.chained and self.isChained(self.f) == None and self.isChained(self.g) == None
      terminatingChain = not self.chained and self.isChained(self.g)
      
      self.log(f"END UNCHAINED {self.name}") if terminatingUnchained else None
      self.log(f"END CHAINED") if terminatingChain else None
      
      shouldUnpackResult = (terminatingChain or terminatingUnchained)
      
      if shouldUnpackResult:      
        r = r[0]
      
      self.log(f"------------------------------------ __call__ end {self.__getType(self)}")
      return r
    except Exception as inst:
      self.log(f"EXCEPTION -------- {type(inst)} {inst}")
      raise inst
      
#rules:
#always return a new composition
#where the current composer is f, and other is g
#f may always be
  def __or__(self, other):
#    self.log(f"COMPOSE::::::::: {self} | {other.name}")
    self.log(f"COMPOSE::::::::: {self.name}+ | {other.name}")
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

