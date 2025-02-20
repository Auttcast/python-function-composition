from typing import Callable, Optional
import inspect

class Composable:

  def __init__(self, func):
    self.__isData = not isinstance(func, Callable)
    self.f = func
    self.g = None
    self.__chained = False

  @staticmethod
  def __invokeNative(func, args):
    result = func(*args)
    #todo op comparison
    if type(result) not in [type((1,)), type(None)]: result = (result,)
    return result

  @staticmethod
  def __invokeCompose(func, args):
    return func(*args) if args is not None else func()

  @staticmethod
  def __internal_call(f, g, args):
    invokeF = Composable.__invokeCompose if isinstance(f, Composable) else Composable.__invokeNative
    result = invokeF(f, args)
    
    if g is not None:
      invokeG = Composable.__invokeCompose if isinstance(g, Composable) else Composable.__invokeNative
      result = invokeG(g, result)

    return result

  @staticmethod
  def __isChained(target) -> Optional[bool]:
    if target is None: return None
    if not isinstance(target, Composable): return None
    return target.__chained

  @staticmethod
  def __isTerminating(f, g):
      gChainState = Composable.__isChained(g)
      if gChainState: return True
      return Composable.__isChained(f) is None and gChainState is None #is unchained
    
  def __call__(self, *args):
    if self.__isData: return self.f

    result = Composable.__internal_call(self.f, self.g, args)
    isSingleTuple = type(result) == tuple and len(result) == 1
    isTerminating = not self.__chained and Composable.__isTerminating(self.f, self.g)
    shouldUnpackResult = isTerminating and isSingleTuple

    if shouldUnpackResult:
      result = result[0]

    return result

  @staticmethod
  def __internalFactory(func): return Composable(func)

  #composition operator
  def __or__(self, other):
    if not isinstance(other, Composable): other = Composable.__internalFactory(other)

    newComp = Composable.__internalFactory(self)
    newComp.__isData = self.__isData
    self.__chained = True
    newComp.__chained = False
    otherComp = Composable.__internalFactory(other.f)
    otherComp.__chained = True
    otherComp.__isData = self.__isData
    newComp.g = otherComp

    return newComp

  @staticmethod
  def __getParamCount(func):
    if isinstance(func, Composable): return Composable.__getParamCount(func.f)
    if inspect.isclass(func): return len(inspect.signature(func.__call__).parameters)
    return len(inspect.signature(func).parameters)

  @staticmethod
  def __curry_inline(fleft, fright, argCount):
    match argCount:
      case 2: return Composable.__internalFactory(lambda x: fleft(fright, x))
      case 3: return Composable.__internalFactory(lambda x1, x2: fleft(fright, x1, x2))
      case 4: return Composable.__internalFactory(lambda x1, x2, x3: fleft(fright, x1, x2, x3))
      case 5: return Composable.__internalFactory(lambda x1, x2, x3, x4: fleft(fright, x1, x2, x3, x4))
      case 6: return Composable.__internalFactory(lambda x1, x2, x3, x4, x5: fleft(fright, x1, x2, x3, x4, x5))
      case 7: return Composable.__internalFactory(lambda x1, x2, x3, x4, x5, x6: fleft(fright, x1, x2, x3, x4, x5, x6))
      case 8: return Composable.__internalFactory(lambda x1, x2, x3, x4, x5, x6, x7: fleft(fright, x1, x2, x3, x4, x5, x6, x7))
      case _: raise f"unsupported argument count {argCount}"
        
  #partial application operator
  def __and__(self, other):
    selfArgCount = self.__getParamCount(self)
    assumeNested = selfArgCount == 1
    
    if assumeNested: 
      return Composable.__internalFactory(lambda x: self(other)(x))
    return self.__curry_inline(self, other, selfArgCount)

  #invocation operator
  def __lt__(self, other):
    data = other.f
    nextFunc = self
    result = nextFunc(data)
    if isinstance(result, tuple) and len(result) == 1:
      result = result[0]
    return result
