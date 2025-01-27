from typing import Callable
from collections.abc import Iterable

#RULES:
#Composer has two objectives
#1: wrap lambdas in composable functionality: f
#2: optionally contain another composed function: g

#g will only exist if Composable was created from a chain

class Composable:

  def __init__(self, func):
    self.f = func
    self.g = None
    self.chained = False
#    self.f: Callable[[()], ()] = func
#    self.g: Callable[[()], ()] = nextFunc
    
  def log(self, message):
    if True:
      print(f"DEBUG {self.__hash__()} {message}")
    
  def _invoke(self, func, name, args):
    funcType = "compose" if type(func) == type(self) else "func"
    #self.log(f"BEFORE {funcType} {name}({args}) |||  {func.__hash__()}")
    
    r = func(*args) 
    
    if not type(func) == type(self):
      r = (r,)
      #self.log(f"AFTER  {funcType} {name}({args}) -> {r}  ||| hash{func.__hash__()} ")
    
    return r
  
  def _internal_call(self, args):
    fr = self._invoke(self.f, "f", args)
    result = self._invoke(self.g, "g", fr) if not self.g is None else fr  
    return result
    
  def __call__(self, *args):
    try:
      #self.log(f"__call__ in: {args} type(self.f): {type(self.f)} type(self.g): {type(self.g)} -----------------")
      r = self._internal_call(args)
      #r = r[0]
      #self.log(f"__call__ out: {r}")
#      if self.g is not None:
#        self.log(f"CHAINS (self, f, g) ({self.chained}, {self.f.chained}, {self.g.chained})")
        
#      if type(self.f) is type(Composable):
      
      shouldUnpackResult = self.g is not None and not self.chained and not self.g.chained
      if shouldUnpackResult: r = r[0]
      
      return r
    except Exception as inst:
      self.log(f"EXCEPTION -------- {type(inst)} {inst}")
      raise inst
      
#rules:
#always return a new composition
#where the current composer is f, and other is g
#f may always be
  def __or__(self, other):
#    self.log(f"COMPOSE::::::::: {self.name} | {other.name}")
#    self.log(f"COMPOSE::::::::: {self} | {other.name}")
    if isinstance(other, Composable):
        newComp = Composable(self)
        otherComp = Composable(other.f)
        newComp.g = otherComp
        newComp.f.chained = True
        return newComp
    else:
        raise TypeError(f"Unsupported operand type(s) for |: 'Composable' and '{type(other).__name__}'")

