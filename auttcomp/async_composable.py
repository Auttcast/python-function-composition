from typing import Any, Awaitable, Callable, Concatenate, Optional, ParamSpec, TypeVar, Generic
import inspect

_INV_R_TYPE_PACK = {type((1,)), type(None)}

#AsyncComposable
P = ParamSpec('P')
R = TypeVar('R')
OR = TypeVar('OR')

#partial app
P2 = ParamSpec('P2')
R2 = TypeVar('R2')
A = TypeVar('A')

#invocation
IT = TypeVar('IT')
IR = TypeVar('IR')

class AsyncComposable(Generic[P, R]):

    def __init__(self, func:Callable[P, Awaitable[R]]):
        self.__f:Callable[P, Awaitable[R]] = func
        self.__g = None
        self.__chained = False

    #composition operator
    def __or__(self, other:Callable[[Any], Awaitable[OR]]) -> Callable[P, Awaitable[OR]]:
        
        self_clone = AsyncComposable(self.__f)
        self_clone.__g = self.__g
        self_clone.__chained = self.__chained

        new_comp = AsyncComposable(self_clone)
        self_clone.__chained = True
        new_comp.__chained = False
        other_comp = None
        if isinstance(other, AsyncComposable):
            other_comp = AsyncComposable(other.__f)
            other_comp.__g = other.__g
        else:
            other_comp = AsyncComposable(other)
        other_comp.__chained = True
        new_comp.__g = other_comp

        return new_comp

    def __get_bound_args(sig, args, kwargs):
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        return bound.args

    @staticmethod
    def __get_sig_recurse(func):
        if isinstance(func, AsyncComposable):
            return AsyncComposable.__get_sig_recurse(func.__f)
        else:
            if inspect.isclass(func):
                return inspect.signature(func.__call__)
            return inspect.signature(func)

    __sig = None
    def __get_singleton_sig_f(self):
        return self.__sig if self.__sig is not None else AsyncComposable.__get_sig_recurse(self.__f)

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:

        if len(kwargs.keys()) > 0:
            sig = self.__get_singleton_sig_f()
            args = AsyncComposable.__get_bound_args(sig, args, kwargs)
        
        result = await AsyncComposable.__internal_call(self.__f, self.__g, args)
        is_single_tuple = type(result) == tuple and len(result) == 1
        is_terminating = not self.__chained and AsyncComposable.__is_terminating(self.__f, self.__g)
        should_unpack_result = is_terminating and is_single_tuple

        if should_unpack_result:
            result = result[0]

        return result

    @staticmethod
    def __is_terminating(f, g):
        g_chain_state = AsyncComposable.__is_chained(g)

        if g_chain_state: 
            return True
        
        return AsyncComposable.__is_chained(f) is None and g_chain_state is None #is unchained

    @staticmethod
    async def __internal_call(f, g, args):
        invoke_f = AsyncComposable.__invoke_compose if isinstance(f, AsyncComposable) else AsyncComposable.__invoke_native
        result = await invoke_f(f, args)

        if g is not None:
            invoke_g = AsyncComposable.__invoke_compose if isinstance(g, AsyncComposable) else AsyncComposable.__invoke_native
            result = await invoke_g(g, result)

        return result

    @staticmethod
    async def __invoke_compose(func, args):
        return (await func(*args)) if args is not None else await func()

    @staticmethod
    async def __invoke_native(func, args):
        maybe_co = func(*args) #co or async_gen
        
        result = await maybe_co if inspect.iscoroutine(maybe_co) else maybe_co

        if type(result) not in _INV_R_TYPE_PACK:
            result = (result,)

        return result

    @staticmethod
    def __is_chained(target) -> Optional[bool]:
        if target is None: 
            return None
        
        if not isinstance(target, AsyncComposable): 
            return None
        
        return target.__chained

    #partial application operator
    def __and__(self:Callable[Concatenate[A, P2], Awaitable[R2]], param:A) -> Callable[P2, Awaitable[R2]]:
        arg_count = len(self.__get_singleton_sig_f().parameters)
        return AsyncComposable._PartialApp._bind(self, param, arg_count)

    class _PartialApp:

        @staticmethod
        def _bind(func, param, arg_count):
            match arg_count:
                case 1: return AsyncComposable(lambda: func(param))()
                case 2: return AsyncComposable(lambda x: func(param, x))
                case 3: return AsyncComposable(lambda x1, x2: func(param, x1, x2))
                case 4: return AsyncComposable(lambda x1, x2, x3: func(param, x1, x2, x3))
                case 5: return AsyncComposable(lambda x1, x2, x3, x4: func(param, x1, x2, x3, x4))
                case 6: return AsyncComposable(lambda x1, x2, x3, x4, x5: func(param, x1, x2, x3, x4, x5))
                case 7: return AsyncComposable(lambda x1, x2, x3, x4, x5, x6: func(param, x1, x2, x3, x4, x5, x6))
                case 8: return AsyncComposable(lambda x1, x2, x3, x4, x5, x6, x7: func(param, x1, x2, x3, x4, x5, x6, x7))
                case _: raise TypeError(f"unsupported argument count {arg_count}")

    #invocation operator
    def __lt__(next_func_async, id_func):
        return next_func_async(id_func())
    
