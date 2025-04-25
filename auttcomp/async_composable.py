from .composable import get_argc
from typing import Any, Awaitable, Callable, Concatenate, ParamSpec, TypeVar, Generic
import inspect

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
        self.__funcs = (func,)
        self.__arg_count = None #lazy loaded via get_singleton_argc

    def get_singleton_argc(self):
        if self.__arg_count:
            return self.__arg_count
        else:
            self.__arg_count = get_argc(self.__funcs[0])
            return self.__arg_count

    #composition operator
    def __or__(self, other:Callable[[Any], Awaitable[OR]]) -> Callable[P, Awaitable[OR]]:
        
        new_comp = AsyncComposable(None)
        new_comp.__arg_count = self.get_singleton_argc()

        if isinstance(other, AsyncComposable):
            new_comp.__funcs = (*self.__funcs, *other.__funcs)
        else:
            new_comp.__funcs = (*self.__funcs, other)

        return new_comp

    @staticmethod
    async def co_or_gen(maybe_co_or_gen):
        if inspect.iscoroutine(maybe_co_or_gen):
            return await maybe_co_or_gen
        return maybe_co_or_gen

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:

        #first invocation args and kwargs
        if args and not kwargs:
            result_co = self.__funcs[0](*args)
        elif args and kwargs:
            result_co = self.__funcs[0](*args, **kwargs)
        elif not args and kwargs:
            result_co = self.__funcs[0](**kwargs)
        else:
            result_co = self.__funcs[0]()

        #all other invocations, expecting naturally bound args via composition
        for func in self.__funcs[1:]:
            result = await AsyncComposable.co_or_gen(result_co)
            if result.__class__ == tuple:
                result_co = func(*result)
            else:
                result_co = func(result)
            
        return await AsyncComposable.co_or_gen(result_co)

    @staticmethod
    def __partial_app_comp_factory(func, argc):
        comp = AsyncComposable(None)
        comp.__funcs = (func,)
        comp.__arg_count = argc - 1 #avoids a call to inspect
        return comp

    #partial application operator
    def __and__(self:Callable[Concatenate[A, P2], R2], param:A) -> Callable[P2, R2]:
        argc = self.get_singleton_argc()
        match argc:
            case 1: return self(param) #must invoke when all params are applied
            case 2: return AsyncComposable.__partial_app_comp_factory(lambda x: self(param, x), argc)
            case 3: return AsyncComposable.__partial_app_comp_factory(lambda x1, x2: self(param, x1, x2), argc)
            case 4: return AsyncComposable.__partial_app_comp_factory(lambda x1, x2, x3: self(param, x1, x2, x3), argc)
            case 5: return AsyncComposable.__partial_app_comp_factory(lambda x1, x2, x3, x4: self(param, x1, x2, x3, x4), argc)
            case 6: return AsyncComposable.__partial_app_comp_factory(lambda x1, x2, x3, x4, x5: self(param, x1, x2, x3, x4, x5), argc)
            case 7: return AsyncComposable.__partial_app_comp_factory(lambda x1, x2, x3, x4, x5, x6: self(param, x1, x2, x3, x4, x5, x6), argc)
            case 8: return AsyncComposable.__partial_app_comp_factory(lambda x1, x2, x3, x4, x5, x6, x7: self(param, x1, x2, x3, x4, x5, x6, x7), argc)
            case _: raise TypeError(f"unsupported argument count {argc}")

    #invocation operator
    def __lt__(next_func_async, id_func):
        return next_func_async(id_func())
    
