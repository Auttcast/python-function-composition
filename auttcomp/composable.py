from typing import Any, Callable, Concatenate, ParamSpec, TypeVar, Generic
import inspect

#composable
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

class Composable(Generic[P, R]):

    def __init__(self, func:Callable[P, R] = None):
        self.__funcs = (func,)

    #composition operator
    def __or__(self, other:Callable[[Any], OR]) -> Callable[P, OR]:
        
        new_comp = Composable()

        if isinstance(other, Composable):
            new_comp.__funcs = (*self.__funcs, *other.__funcs)
        else:
            new_comp.__funcs = (*self.__funcs, other)

        return new_comp

    @staticmethod
    def __get_sig(func):
        if inspect.isclass(func):
            return inspect.signature(func.__call__)
        return inspect.signature(func)

    __sig = None
    def __get_singleton_sig_f(self):
        if self.__sig is not None:
            return self.__sig
        else:
            self.__sig = Composable.__get_sig(self.__funcs[0])
            return self.__sig

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:

        #first invocation must unpack from __call__
        if args and not kwargs:
            result = self.__funcs[0](*args)
        elif args and kwargs:
            result = self.__funcs[0](*args, **kwargs)
        elif not args and kwargs:
            result = self.__funcs[0](**kwargs)
        else:
            result = self.__funcs[0]()

        #all other invocations, expecting naturally bound args via composition
        for func in self.__funcs[1:]:
            if result.__class__ == tuple:
                result = func(*result)
            else:
                result = func(result)
            
        return result

    #partial application operator
    def __and__(self:Callable[Concatenate[A, P2], R2], param:A) -> Callable[P2, R2]:
        arg_count = len(self.__get_singleton_sig_f().parameters)
        return Composable._PartialApp._bind(self, param, arg_count)

    class _PartialApp:

        @staticmethod
        def _bind(func, param, arg_count):
            match arg_count:
                case 1: return func(param)
                case 2: return Composable(lambda x: func(param, x))
                case 3: return Composable(lambda x1, x2: func(param, x1, x2))
                case 4: return Composable(lambda x1, x2, x3: func(param, x1, x2, x3))
                case 5: return Composable(lambda x1, x2, x3, x4: func(param, x1, x2, x3, x4))
                case 6: return Composable(lambda x1, x2, x3, x4, x5: func(param, x1, x2, x3, x4, x5))
                case 7: return Composable(lambda x1, x2, x3, x4, x5, x6: func(param, x1, x2, x3, x4, x5, x6))
                case 8: return Composable(lambda x1, x2, x3, x4, x5, x6, x7: func(param, x1, x2, x3, x4, x5, x6, x7))
                case _: raise TypeError(f"unsupported argument count {arg_count}")

    #invocation operator
    def __lt__(next_func:Callable[[IT], IR], id_func:Callable[[], IT]) -> IR:
        return next_func(id_func())
        