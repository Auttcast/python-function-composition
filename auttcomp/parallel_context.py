from typing import Any, Callable, Iterable
from auttcomp.composable import Composable
from concurrent.futures import ThreadPoolExecutor

def id_param(x:Any) -> Any:
    return x

class ParallelApi:

    def __init__(self, pool:ThreadPoolExecutor):
        self.pool:ThreadPoolExecutor = pool

    def map[T, R](self, func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[R]]:
        
        @Composable
        def partial_map(data: Iterable[T]) -> Iterable[R]:
            return self.pool.map(func, data)

        return partial_map

    def filter[T, R](self, func: Callable[[T], R] = id_param) -> Callable[[Iterable[T]], Iterable[T]]:
        
        @Composable
        def partial_filter(data: Iterable[T]) -> Iterable[T]:
            lift = self.pool.map(lambda x: (x, func(x)), data)
            lift_filter = filter(lambda x: x[1], lift)
            lift_return = map(lambda x: x[0], lift_filter)
            return lift_return

        return partial_filter
    
    def list[T](self, data: Iterable[T]) -> list[T]:
        return list(data)


class ParallelContext:
    def __init__(self, pool:ThreadPoolExecutor):
        self.pool:ThreadPoolExecutor = pool

    def __call__(self, composition:Callable[[ParallelApi], Composable]) -> Composable:
        return composition(ParallelApi(self.pool))
