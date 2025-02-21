from typing import Callable, Optional
import inspect

_INV_R_TYPE_PACK = [type((1,)), type(None)]

class Composable:

  def __init__(self, func):
    self.__isData = not isinstance(func, Callable)
    self.f = func
    self.g = None
    self.__chained = False

  #composition operator
  def __or__(self, other):
    if not isinstance(other, Composable): other = Composable(other)

    newComp = Composable(self)
    newComp.__isData = self.__isData
    self.__chained = True
    newComp.__chained = False
    otherComp = Composable(other.f)
    otherComp.__chained = True
    otherComp.__isData = self.__isData
    newComp.g = otherComp

    return newComp

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
  def __isTerminating(f, g):
    gChainState = Composable.__isChained(g)
    if gChainState: return True
    return Composable.__isChained(f) is None and gChainState is None #is unchained

  @staticmethod
  def __internal_call(f, g, args):
    invokeF = Composable.__invokeCompose if isinstance(f, Composable) else Composable.__invokeNative
    result = invokeF(f, args)

    if g is not None:
      invokeG = Composable.__invokeCompose if isinstance(g, Composable) else Composable.__invokeNative
      result = invokeG(g, result)

    return result

  @staticmethod
  def __invokeCompose(func, args):
    return func(*args) if args is not None else func()

  @staticmethod
  def __invokeNative(func, args):
    result = func(*args)
    if type(result) not in _INV_R_TYPE_PACK: result = (result,)
    return result

  @staticmethod
  def __isChained(target) -> Optional[bool]:
    if target is None: return None
    if not isinstance(target, Composable): return None
    return target.__chained

  #partial application operator
  def __and__(self, param): return Composable._PartialApp._apply(self, param)

  class _PartialApp:

    @staticmethod
    def _apply(func, param):
      selfArgCount = Composable._PartialApp.__getParamCount(func)
      return Composable._PartialApp.__apply_inline(func, param, selfArgCount)

    @staticmethod
    def __apply_inline(func, param, argCount):
      match argCount:
        case 1: return Composable(lambda: func(param))
        case 2: return Composable(lambda x: func(param, x))
        case 3: return Composable(lambda x1, x2: func(param, x1, x2))
        case 4: return Composable(lambda x1, x2, x3: func(param, x1, x2, x3))
        case 5: return Composable(lambda x1, x2, x3, x4: func(param, x1, x2, x3, x4))
        case 6: return Composable(lambda x1, x2, x3, x4, x5: func(param, x1, x2, x3, x4, x5))
        case 7: return Composable(lambda x1, x2, x3, x4, x5, x6: func(param, x1, x2, x3, x4, x5, x6))
        case 8: return Composable(lambda x1, x2, x3, x4, x5, x6, x7: func(param, x1, x2, x3, x4, x5, x6, x7))
        case _: raise TypeError(f"unsupported argument count {argCount}")

    @staticmethod
    def __getParamCount(func):
      if isinstance(func, Composable): return Composable._PartialApp.__getParamCount(func.f)
      if inspect.isclass(func): return len(inspect.signature(func.__call__).parameters)
      return len(inspect.signature(func).parameters)

  #invocation operator
  def __lt__(self, compObj):
    nextFunc = self
    data = compObj.f
    result = nextFunc(data)
    if isinstance(result, tuple) and len(result) == 1:
      result = result[0]
    return result
