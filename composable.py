from typing import Callable, Optional

#todo
#wrap modules/classes, decorators
#type hinting?

class Composable:

  enableLogging = False

  def __init__(self, func: Callable):
    self.f = func
    self.g = None
    self.chained = False
    
  def log(self, message):
    if self.enableLogging:
      print(f"DEBUG {self.__hash__()} {message}")
    
  def __isComposable(self, target): return type(target) == type(self)
    
  def isChained(self, target) -> Optional[bool]:
    if target is None: return None
    if not self.__isComposable(target): return None
    return target.chained
    
  def __invokeNative(self, func, name, args):
    self.log(f"START FUNCTION ----------------- {args}")
    
    r = func(*args)
    if type(r) not in [type((1,)), type(None)]: r = (r,)
    
    self.log(f"END FUNCTION   ----------------- {args} -> {r}")
    return r
  
  def __invokeCompose(self, func, name, args):
    #self.log(f"START COMPOSE -----------------{name} {args}")
    r = func(*args) if args is not None else func()
    #self.log(f"END COMPOSE -----------------{name} {args} -> {r}")
    return r
  
  def __internal_call(self, args):
  
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
    try:
    
      r = self.__internal_call(args)
 
      (terminatingUnchained, terminatingChain) = self.__getChainState()
      
      isSingleTuple = type(r) == type((1,)) and len(r) == 1
      shouldUnpackResult = (terminatingChain or terminatingUnchained) and isSingleTuple
      
      if (shouldUnpackResult):
        r = r[0]
      
      return r
    except Exception as inst:
      self.log(f"EXCEPTION -------- {type(inst)} {inst}")
      raise inst
      
  def __or__(self, other):
    if self.__isComposable(other):
        newComp = Composable(self)
        self.chained = True
        newComp.chained = False
        otherComp = Composable(other.f)
        otherComp.chained = True
        newComp.g = otherComp
        return newComp
    else:
        raise TypeError(f"Unsupported operand type(s) for |: 'Composable' and '{type(other).__name__}'")

