from typing import Callable
from collections.abc import Iterable

#RULES:
#calling func(*args) requires args to be a collection
#all args received from __call__ will be wrapped in (,)
#note, the call chain will be a mixture of composers and user-lambdas, with a mixture of requirements
#results from user f or g should be wrapped in (,) as a form of normalization

class Composable:

  def __init__(self, func, nextFunc=None, parentComp=None):
    self.parentComp = parentComp
    self.f = func
    self.g = nextFunc
#    self.f: Callable[[()], ()] = func
#    self.g: Callable[[()], ()] = nextFunc
    
  def log(self, message):
    if True:
      print(f"DEBUG {message}")
    
  def isMain(self): return self.parentComp == None
    
  def _invoke(self, func, name, args):
    funcType = "compose" if type(func) == type(self) else "func"
    #self.log(f"BEFORE {funcType} {name}({args}) |||  {func.__hash__()}")
    
    r = func(*args) 
    
    if not type(func) == type(self):
      r = (r,)
      self.log(f"AFTER  {funcType} {name}({args}) -> {r}  ||| hash{func.__hash__()} ")
    
    return r
  
  def _internal_call(self, args):
    fr = self._invoke(self.f, "f", args)
    result = self._invoke(self.g, "g", fr) if not self.g is None else fr  
    return result
    
  def __call__(self, *args):
    try:
      self.log(f"________ isMain: {self.isMain()} g: {self.parentComp}")
      
      r = self._internal_call(args)
      
      if self.isMain():
        self.log(f"UNPACKING {r}")
        #return r #unpack args on last call
      r = r
      self.log(f"__call__ RETURN: {r} {type(r)} has g: {not self.g is None}")
      return r
    except Exception as inst:
      self.log(f"EXCEPTION -------- {type(inst)} {inst}")
      raise inst
      
  def __or__(self, other):
    if isinstance(other, Composable):
        return Composable(self, other.f, parentComp=self)
    else:
        raise TypeError(f"Unsupported operand type(s) for |: 'Composable' and '{type(other).__name__}'")

