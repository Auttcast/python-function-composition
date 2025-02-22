from typing import Callable, Concatenate, Optional, ParamSpec, TypeVar, Generic
import inspect

_INV_R_TYPE_PACK = {type((1,)), type(None)}

#composable
P = ParamSpec('P')
R = TypeVar('R')

#partial app
P2 = ParamSpec('P2')
R2 = TypeVar('R2')
A = TypeVar('A')

#invocation
IT = TypeVar('IT')
IR = TypeVar('IR')

class Composable(Generic[P, R]):

  def __init__(self, func:Callable[P, R]):
    self.f:Callable[P, R] = func
    self.g = None
    self.__chained = False

  #composition operator
  def __or__(self, other):
    if not isinstance(other, Composable):
      other = Composable(other)

    new_comp = Composable(self)
    self.__chained = True
    new_comp.__chained = False
    other_comp = Composable(other.f)
    other_comp.__chained = True
    new_comp.g = other_comp

    return new_comp

  def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:

    result = Composable.__internal_call(self.f, self.g, args)
    is_single_tuple = type(result) == tuple and len(result) == 1
    is_terminating = not self.__chained and Composable.__is_terminating(self.f, self.g)
    should_unpack_result = is_terminating and is_single_tuple

    if should_unpack_result:
      result = result[0]

    return result

  @staticmethod
  def __is_terminating(f, g):
    g_chain_state = Composable.__is_chained(g)

    if g_chain_state: 
      return True
    
    return Composable.__is_chained(f) is None and g_chain_state is None #is unchained

  @staticmethod
  def __internal_call(f, g, args):
    invoke_f = Composable.__invoke_compose if isinstance(f, Composable) else Composable.__invoke_native
    result = invoke_f(f, args)

    if g is not None:
      invoke_g = Composable.__invoke_compose if isinstance(g, Composable) else Composable.__invoke_native
      result = invoke_g(g, result)

    return result

  @staticmethod
  def __invoke_compose(func, args):
    return func(*args) if args is not None else func()

  @staticmethod
  def __invoke_native(func, args):
    result = func(*args)

    if type(result) not in _INV_R_TYPE_PACK:
      result = (result,)

    return result

  @staticmethod
  def __is_chained(target) -> Optional[bool]:
    if target is None: 
      return None
    
    if not isinstance(target, Composable): 
      return None
    
    return target.__chained

  #partial application operator
  def __and__(self:Callable[Concatenate[A, P2], R2], param:A) -> Callable[P2, R2]:
    return Composable._PartialApp._part_apply(self, param)

  class _PartialApp:

    @staticmethod
    def _part_apply(func, param):
      self_arg_count = Composable._PartialApp.__get_param_count(func)
      return Composable._PartialApp.__apply_inline(func, param, self_arg_count)

    @staticmethod
    def __apply_inline(func, param, arg_count):
      match arg_count:
        case 1: return Composable(lambda: func(param))
        case 2: return Composable(lambda x: func(param, x))
        case 3: return Composable(lambda x1, x2: func(param, x1, x2))
        case 4: return Composable(lambda x1, x2, x3: func(param, x1, x2, x3))
        case 5: return Composable(lambda x1, x2, x3, x4: func(param, x1, x2, x3, x4))
        case 6: return Composable(lambda x1, x2, x3, x4, x5: func(param, x1, x2, x3, x4, x5))
        case 7: return Composable(lambda x1, x2, x3, x4, x5, x6: func(param, x1, x2, x3, x4, x5, x6))
        case 8: return Composable(lambda x1, x2, x3, x4, x5, x6, x7: func(param, x1, x2, x3, x4, x5, x6, x7))
        case _: raise TypeError(f"unsupported argument count {arg_count}")

    @staticmethod
    def __get_param_count(func):
      if isinstance(func, Composable):
        return Composable._PartialApp.__get_param_count(func.f)
      
      if inspect.isclass(func): 
        return len(inspect.signature(func.__call__).parameters)
      
      return len(inspect.signature(func).parameters)

  #invocation operator
  def __lt__(next_func:Callable[[IT], IR], id_func:Callable[[], IT]):
    return next_func(id_func())
    