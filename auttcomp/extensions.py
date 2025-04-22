from .utility import ObjUtil
from .composable import Composable, P, R
from typing import Callable, Any, Tuple, Iterable, TypeVar
from .common import id_param, KeyValuePair
from shape_eval.service import shape as eval_shape
import functools
import itertools

T = TypeVar('T')
T2 = TypeVar('T2')
K = TypeVar('K')

class Api(Composable[P, R]):

    @staticmethod
    @Composable
    def id(data: T) -> Callable[[], T]:
        '''create an identity function for the given data'''

        @Composable
        def partial_id() -> T:
            return data

        return partial_id

    @staticmethod
    @Composable
    def shape(obj:Any) -> Any:
        return eval_shape(obj)

    @staticmethod
    @Composable
    def map(func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[R]]:
        '''curried version of python's map:
        map(func, *iterables) --> map object\n\nMake an iterator that computes the function using arguments from\neach of the iterables.    Stops when the shortest iterable is exhausted.
        '''

        @Composable
        def partial_map(data: Iterable[T]) -> Iterable[R]:
            return map(func, data)

        return partial_map

    @staticmethod
    @Composable
    def foreach(func: Callable[[T], R]) -> Callable[[Iterable[T]], None]:
        '''exec the func for each element in the iterable'''

        @Composable
        def partial_foreach(data: Iterable[T]) -> None:
            for x in data:
                func(x)

        return partial_foreach

    @staticmethod
    @Composable
    def filter(func: Callable[[T], R] = id_param) -> Callable[[Iterable[T]], Iterable[T]]:
        '''curried version of python's filter
        filter(function or None, iterable) --> filter object\n\nReturn an iterator yielding those items of iterable for which function(item)\nis true. If function is None, return the items that are true.
        '''

        @Composable
        def partial_filter(data: Iterable[T]) -> Iterable[T]:
            return filter(func, data)

        return partial_filter

    @staticmethod
    @Composable
    def reduce(func: Callable[[T, T], R], initial: T = None) -> Callable[[Iterable[T]], R]:
        '''curried version of functools's reduce
        reduce(function, iterable) -> value\n\nApply a function of two arguments cumulatively to the items of an iterable, from left to right.\n\nThis effectively reduces the iterable to a single value.    If initial is present,\nit is placed before the items of the iterable in the calculation, and serves as\na default when the iterable is empty.\n\nFor example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])\ncalculates ((((1 + 2) + 3) + 4) + 5).
        '''

        @Composable
        def partial_reduce(data: Iterable[T]) -> R:
            if initial is None:
                return functools.reduce(func, data)
            else:
                return functools.reduce(func, data, initial)

        return partial_reduce

    @staticmethod
    @Composable
    def list(data: Iterable[T]) -> list[T]:
        '''Built-in mutable sequence.\n\nIf no argument is given, the constructor creates a new empty list.\nThe argument must be an iterable if specified.'''
        return list(data)

    @staticmethod
    @Composable
    def distinct(data: Iterable[T]) -> Iterable[T]:
        '''a general purpose distinct implementation where performance is not required
        if your data is compatible, you may be able to use distinctSet
        '''

        return list(functools.reduce(lambda a, b: a + [b] if b not in a else a, data, []))

    @staticmethod
    @Composable
    def distinct_set(data: Iterable[T]) -> Iterable[T]:
        '''implementation of distinct using python's set, but limited to qualifying primitive types'''
        return list(set(data))

    @staticmethod
    @Composable
    def flatmap(func: Callable[[T], R] = id_param) -> Callable[[Iterable[Iterable[T]]], Iterable[R]]:
        '''iterable implementation of flatmap'''

        @Composable
        def partial_flatmap(data: Iterable[Iterable[T]]) -> Iterable[R]:
            for ys in map(func, data):
                for y in ys:
                    yield y

        return partial_flatmap

    @staticmethod
    @Composable
    def any(func: Callable[[T], R] = id_param) -> Callable[[Iterable[T]], bool]:
        '''curried version of python's any function. Returns True if any element satisfies the condition'''

        @Composable
        def partial_any(data: Iterable[T]) -> bool:
            return any(map(func, data))

        return partial_any

    @staticmethod
    @Composable
    def all(func: Callable[[T], R] = id_param) -> Callable[[Iterable[T]], bool]:
        '''curried version of python's any function. Returns True if all elements satisfy the condition'''

        @Composable
        def partial_all(data: Iterable[T]) -> bool:
            return all(map(func, data))

        return partial_all

    @staticmethod
    @Composable
    def reverse(data: Iterable[T]) -> Iterable[T]:
        '''python's reverse'''
        return reversed(ObjUtil.exec_generator(data))

    @staticmethod
    @Composable
    def sort(data: Iterable[T]) -> Iterable[T]:
        '''python's sort'''
        return sorted(ObjUtil.exec_generator(data))

    @staticmethod
    @Composable
    def sort_by(func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[T]]:
        '''curried version of python's sort with key selector'''

        @Composable
        def partial_sort_by(data: Iterable[T]) -> Iterable[T]:
            return sorted(ObjUtil.exec_generator(data), key=func)

        return partial_sort_by

    @staticmethod
    @Composable
    def sort_by_desc(func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[T]]:
        '''curried version of python's sort w/ key selector followed by reverse'''

        @Composable
        def partial_sort_by_desc(data: Iterable[T]) -> Iterable[T]:
            return sorted(ObjUtil.exec_generator(data), key=func, reverse=True)

        return partial_sort_by_desc

    @staticmethod
    @Composable
    def take(count: int) -> Callable[[Iterable[T]], Iterable[T]]:
        '''basically yielded list[0:count]'''

        @Composable
        def partial_take(data: Iterable[T]) -> Iterable[T]:
            iter_count = 0
            for x in data:
                iter_count += 1
                if iter_count > count:
                    break
                yield x

        return partial_take

    @staticmethod
    @Composable
    def skip(count: int) -> Callable[[Iterable[T]], Iterable[T]]:
        '''basically yielded list[count:]'''

        @Composable
        def partial_skip(data: Iterable[T]) -> Iterable[R]:
            iter_count = 0
            for x in data:
                iter_count += 1
                if iter_count > count:
                    yield x

        return partial_skip

    @staticmethod
    @Composable
    def group(func: Callable[[T], K] = id_param) -> Callable[[Iterable[T]], Iterable[KeyValuePair[K, Iterable[T]]]]:
        '''curried version of itertools.groupby
        sort by key is used before grouping to achieve singular grouping
        this implementation runs the iterable for the grouping, but yields the key/value pair as a new iterable
        '''

        @Composable
        def partial_group(data: Iterable[T]) -> Iterable[KeyValuePair[R, Iterable[T]]]:
            for key, value in itertools.groupby(sorted(ObjUtil.exec_generator(data), key=func), key=func):
                yield KeyValuePair(key, ObjUtil.exec_generator(value))

        return partial_group

    @staticmethod
    @Composable
    def join(
        left_data: Iterable[T],
        left_key_func: Callable[[T], K],
        right_key_func: Callable[[T], K],
        left_value_selector: Callable[[T], Any] = id_param,
        right_value_selector: Callable[[T], Any] = id_param
    ) -> Callable[[T2], Iterable[Tuple[K, Tuple[T, T2]]]]:
        '''(inner join) combine two groups by key'''

        @Composable
        def partial_join(right_data: Iterable[T2]) -> Iterable[Tuple[K, Tuple[T, T2]]]:
            left_group = Api.group(left_key_func)(left_data)
            right_group = Api.group(right_key_func)(right_data)

            tracker = {}
            for lg in left_group:
                tracker[lg.key] = lg.value
            for rg in right_group:
                lv = tracker.get(rg.key)
                if lv is not None:
                    yield rg.key, (list(map(left_value_selector, lv)), list(map(right_value_selector, rg.value)))

        return partial_join

    @staticmethod
    @Composable
    def zip(data:Iterable[T]) -> Callable[[Iterable[T2]], Iterable[Tuple[T2, T]]]:
        '''curried version of itertools.zip_longest'''

        @Composable
        def partial_zip(data2: Iterable[T2]) -> Iterable[Tuple[T2, T]]:
            return itertools.zip_longest(data2, data)
        
        return partial_zip
    
    @staticmethod
    @Composable
    def flatnest(path_selector:Callable[[Any], Any], data_selector:Callable[[Any], Any]) -> Callable[[Any], Iterable[Any]]:
        '''yield properties of a recursive structure by data_selector, following the path_selector'''

        @Composable
        def partial_flatnest(model:Any) -> Iterable[Any]:
            if model is not None:
                yield data_selector(model)
                next = path_selector(model)
                if next is not None:
                    yield from partial_flatnest(next)
                    
        return partial_flatnest

    @staticmethod
    @Composable
    def first(selector:Callable[[Any], Any] = id_param) -> Callable[[Iterable[Any]], Any]:
        '''return the first item found by the selector or None if not found'''

        @Composable
        def partial_first(data:Iterable[Any]):
            for item in data:
                if selector(item):
                    return item
            return None
        
        return partial_first
    
    @staticmethod
    @Composable
    def single(selector:Callable[[Any], Any] = id_param) -> Callable[[Iterable[Any]], Any]:
        '''return a single item determined by the selector and assert that a single item is matched.
        Throws ValueError if the selector matches no items, or more than one item.
        '''

        @Composable
        def partial_single(data:Iterable[Any]):

            found = []

            for item in data:
                if len(found) == 0:
                    if selector(item):
                        found.append(item)
                else:
                    if selector(item):
                        raise ValueError("more than one item found")
            
            if len(found) == 1:
                return found[0]
            
            raise ValueError("no items were found")
    
        return partial_single
    
    @staticmethod
    @Composable
    def chunk(count:int) -> Callable[[Iterable[T]], Iterable[Iterable[T]]]:
    
        @Composable
        def partial_chunk(data:Iterable[T]) -> Iterable[list[T]]:
            
            it = iter(data)

            batch = []
            keep_batching = True
            while keep_batching:
                try:
                    for x in range(0, count):
                        batch.append(next(it))
                except StopIteration:
                    keep_batching = False
                finally:
                    yield batch
                    batch = []

        return partial_chunk
    