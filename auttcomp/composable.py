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


def get_argc(func):
    if inspect.isclass(func):
        return len(inspect.signature(func.__call__).parameters)
    return len(inspect.signature(func).parameters)

class Composable(Generic[P, R]):

    def __init__(self, func:Callable[P, R]):
        self.__funcs = (func,)
        self.__arg_count = None #lazy loaded via get_singleton_argc

    def get_singleton_argc(self):
        if self.__arg_count:
            return self.__arg_count
        else:
            self.__arg_count = get_argc(self.__funcs[0])
            return self.__arg_count

    #composition operator
    def __or__(self, other:Callable[[Any], OR]) -> Callable[P, OR]:
        
        new_comp = Composable(None)
        new_comp.__arg_count = self.get_singleton_argc()

        if isinstance(other, Composable):
            new_comp.__funcs = (*self.__funcs, *other.__funcs)
        else:
            new_comp.__funcs = (*self.__funcs, other)

        return new_comp

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:

        #first invocation args and kwargs
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

    @staticmethod
    def __partial_app_comp_factory(func, argc):
        comp = Composable(None)
        comp.__funcs = (func,)
        comp.__arg_count = argc - 1 #avoids a call to inspect
        return comp

    #partial application operator
    def __and__(self:Callable[Concatenate[A, P2], R2], param:A) -> Callable[P2, R2]:
        argc = self.get_singleton_argc()
        match argc:
            case 1: return self(param) #must invoke when all params are applied
            case 2: return Composable.__partial_app_comp_factory(lambda x: self(param, x), argc)
            case 3: return Composable.__partial_app_comp_factory(lambda x1, x2: self(param, x1, x2), argc)
            case 4: return Composable.__partial_app_comp_factory(lambda x1, x2, x3: self(param, x1, x2, x3), argc)
            case 5: return Composable.__partial_app_comp_factory(lambda x1, x2, x3, x4: self(param, x1, x2, x3, x4), argc)
            case 6: return Composable.__partial_app_comp_factory(lambda x1, x2, x3, x4, x5: self(param, x1, x2, x3, x4, x5), argc)
            case 7: return Composable.__partial_app_comp_factory(lambda x1, x2, x3, x4, x5, x6: self(param, x1, x2, x3, x4, x5, x6), argc)
            case 8: return Composable.__partial_app_comp_factory(lambda x1, x2, x3, x4, x5, x6, x7: self(param, x1, x2, x3, x4, x5, x6, x7), argc)
            case _: raise TypeError(f"unsupported argument count {argc}")

    #invocation operator
    def __lt__(next_func:Callable[[IT], IR], id_func:Callable[[], IT]) -> IR:
        return next_func(id_func())
        