from .quicklog import log
from .utility import normalize, ObjUtil
from .shape_eval import eval_shape
from .composable import Composable, P, R
from typing import Callable, Any, Tuple, Iterable, TypeVar, Generic
from .expression_builder import ExpressionExecutor
from typing import Callable
import functools
import itertools

T = TypeVar('T')
T2 = TypeVar('T2')
K = TypeVar('K')

def comp_wrapper(func:Callable[P, R]) -> Composable[P, R]:
  return Composable(func)

class KeyValue(Generic[K, T]):
  def __init__(self, key: K, value: T):
    self.key: K = key
    self.value: T = value

class Api(Composable[P, R]):

  @staticmethod
  @comp_wrapper
  def id(data: T) -> Callable[[], T]:
    '''create an identity function for the given data'''

    @comp_wrapper
    def partial_id() -> T:
      return data

    return partial_id

  @staticmethod
  @comp_wrapper
  def at(func: Callable[[T], R]) -> Callable[[T], R]:
    '''property selector'''

    @comp_wrapper
    def partial_at(obj: T) -> R:
      return func(normalize(obj))

    return partial_at

  @staticmethod
  @comp_wrapper
  def select(func: Callable[[T], R]) -> Callable[[T], R]:
    '''EXPERIMENTAL (basically working like select/map right now)'''
    exp = ExpressionExecutor(func)

    @comp_wrapper
    def partial_select(obj: T) -> R:
      return exp(normalize(obj))

    return partial_select

  @staticmethod
  @comp_wrapper
  def map(func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[R]]:
    '''curried version of python's map:
    map(func, *iterables) --> map object\n\nMake an iterator that computes the function using arguments from\neach of the iterables.  Stops when the shortest iterable is exhausted.
    '''

    @comp_wrapper
    def partial_map(data: Iterable[T]) -> Iterable[R]:
      return map(lambda x: func(normalize(x)), data)

    return partial_map

  @staticmethod
  @comp_wrapper
  def foreach(func: Callable[[T], R]) -> Callable[[Iterable[T]], None]:
    '''exec the func for each element in the iterable'''
    @comp_wrapper
    def partial_foreach(data: Iterable[T]) -> None:
      for x in data:
        func(normalize(x))

    return partial_foreach

  @staticmethod
  @comp_wrapper
  def filter(func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[T]]:
    '''curried version of python's filter
    filter(function or None, iterable) --> filter object\n\nReturn an iterator yielding those items of iterable for which function(item)\nis true. If function is None, return the items that are true.
    '''

    @comp_wrapper
    def partial_filter(data: Iterable[T]) -> Iterable[T]:
      return filter(lambda x: func(normalize(x)), data)

    return partial_filter

  @staticmethod
  @comp_wrapper
  def reduce(func: Callable[[T, T], R]) -> Callable[[Iterable[T]], R]:
    '''curried version of functools's reduce (to use initial value, use reduce2)
    reduce(function, iterable) -> value\n\nApply a function of two arguments cumulatively to the items of an iterable, from left to right.\n\nThis effectively reduces the iterable to a single value.  If initial is present,\nit is placed before the items of the iterable in the calculation, and serves as\na default when the iterable is empty.\n\nFor example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])\ncalculates ((((1 + 2) + 3) + 4) + 5).
    '''

    @comp_wrapper
    def partial_reduce(data: Iterable[T]) -> R:
      return functools.reduce(func, data)

    return partial_reduce

  @staticmethod
  @comp_wrapper
  def reduce2(func: Callable[[T, T], R], initial: T) -> Callable[[Iterable[T]], R]:
    '''curried version of functools's reduce
    reduce(function, iterable, initial) -> value\n\nApply a function of two arguments cumulatively to the items of an iterable, from left to right.\n\nThis effectively reduces the iterable to a single value.  If initial is present,\nit is placed before the items of the iterable in the calculation, and serves as\na default when the iterable is empty.\n\nFor example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])\ncalculates ((((1 + 2) + 3) + 4) + 5).
    '''

    @comp_wrapper
    def partial_reduce(data: Iterable[T]) -> R:
      return functools.reduce(func, data, initial)

    return partial_reduce

  @staticmethod
  @comp_wrapper
  def list(data: Iterable[T]) -> list[T]:
    '''Built-in mutable sequence.\n\nIf no argument is given, the constructor creates a new empty list.\nThe argument must be an iterable if specified.'''
    return list(data)

  @staticmethod
  @comp_wrapper
  def distinct(data: Iterable[T]) -> Iterable[T]:
    '''a general purpose distinct implementation where performance is not required
    if your data is compatible, you may be able to use distinctSet
    '''

    return list(functools.reduce(lambda a, b: a + [b] if b not in a else a, data, []))

  @staticmethod
  @comp_wrapper
  def distinct_set(data: Iterable[T]) -> Iterable[T]:
    '''implementation of distinct using python's set, but limited to qualifying primitive types'''
    return list(set(data))

  @staticmethod
  @comp_wrapper
  def flatmap(func: Callable[[T], R]) -> Callable[[Iterable[Iterable[T]]], Iterable[R]]:
    '''iterable implementation of flatmap'''

    @comp_wrapper
    def partial_flatmap(data: Iterable[Iterable[T]]) -> Iterable[R]:
      for ys in map(lambda x: func(normalize(x)), data):
        for y in ys:
          yield y

    return partial_flatmap

  @staticmethod
  @comp_wrapper
  def flatmapid(data: Iterable[Iterable[T]]) -> Iterable[T]:
    '''shortcut for flatmap(identity func)'''
    return Api.flatmap(lambda x: x)(data)

  @staticmethod
  @comp_wrapper
  def shape(data: Any) -> Any:
    '''evaluates the shape of data, returns a shape object'''
    return eval_shape(data)

  @staticmethod
  @comp_wrapper
  def any(func: Callable[[T], R]) -> Callable[[Iterable[T]], bool]:
    '''curried version of python's any function. Returns True if any element satisfies the condition'''
    @comp_wrapper
    def partial_any(data: Iterable[T]) -> bool:
      return any(map(lambda x: func(normalize(x)), data))

    return partial_any

  @staticmethod
  @comp_wrapper
  def all(func: Callable[[T], R]) -> Callable[[Iterable[T]], bool]:
    '''curried version of python's any function. Returns True if all elements satisfy the condition'''
    @comp_wrapper
    def partial_all(data: Iterable[T]) -> bool:
      return all(map(lambda x: func(normalize(x)), data))

    return partial_all

  @staticmethod
  @comp_wrapper
  def reverse(data: Iterable[T]) -> Iterable[T]:
    '''python's reverse'''
    return reversed(ObjUtil.exec_generator(data))

  @staticmethod
  @comp_wrapper
  def sort(data: Iterable[T]) -> Iterable[T]:
    '''python's sort'''
    return sorted(ObjUtil.exec_generator(data))

  @staticmethod
  @comp_wrapper
  def sort_by(func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[T]]:
    '''curried version of python's sort with key selector'''

    @comp_wrapper
    def partial_sort_by(data: Iterable[T]) -> Iterable[T]:
      return sorted(ObjUtil.exec_generator(data), key=func)

    return partial_sort_by

  @staticmethod
  @comp_wrapper
  def sort_by_descending(func: Callable[[T], R]) -> Callable[[Iterable[T]], Iterable[T]]:
    '''curried version of python's sort w/ key selector followed by reverse'''

    @comp_wrapper
    def partial_sort_by_descending(data: Iterable[T]) -> Iterable[T]:
      return sorted(ObjUtil.exec_generator(data), key=func, reverse=True)

    return partial_sort_by_descending

  @staticmethod
  @comp_wrapper
  def take(count: int) -> Callable[[Iterable[T]], Iterable[T]]:
    '''basically yielded list[0:count]'''

    @comp_wrapper
    def partial_take(data: Iterable[T]) -> Iterable[T]:
      iter_count = 0
      for x in data:
        iter_count += 1
        if iter_count > count:
          break
        yield x

    return partial_take

  @staticmethod
  @comp_wrapper
  def skip(count: int) -> Callable[[Iterable[T]], Iterable[T]]:
    '''basically yielded list[count:]'''

    @comp_wrapper
    def partial_skip(data: Iterable[T]) -> Iterable[R]:
      iter_count = 0
      for x in data:
        iter_count += 1
        if iter_count > count:
          yield x

    return partial_skip

  @staticmethod
  @comp_wrapper
  def group(func: Callable[[T], K]) -> Callable[[Iterable[T]], Iterable[KeyValue[K, Iterable[T]]]]:
    '''curried version of itertools.groupby
    sort by key is used before grouping to achieve singular grouping
    f.groupby(lambda x.property)
    this implementation runs the iterable for the grouping, but yields the key/value pair as a new iterable
    '''

    @comp_wrapper
    def partial_group(data: Iterable[T]) -> Iterable[KeyValue[R, Iterable[T]]]:
      for key, value in itertools.groupby(sorted(ObjUtil.exec_generator(data), key=func, reverse=True), key=func):
        yield KeyValue(key, ObjUtil.exec_generator(value))

    return partial_group

  @staticmethod
  @comp_wrapper
  def inner_join(
    left_data: Iterable[T],
    left_key_func: Callable[[T], K],
    right_key_func: Callable[[T], K],
    left_value_selector: Callable[[T], R],
    right_value_selector: Callable[[T], R]
  ) -> Callable[[T2], Iterable[Tuple[K, Tuple[Iterable[T], Iterable[T2]]]]]:
    '''combine two groups by key
    '''

    if left_value_selector is None: left_value_selector = lambda x: x
    if right_value_selector is None: right_value_selector = lambda x: x

    @comp_wrapper
    def partial_inner_join(right_data: Iterable[T2]) -> Iterable[Tuple[K, Tuple[T, T2]]]:
      left_group = Api.group(left_key_func)(left_data)
      right_group = Api.group(right_key_func)(right_data)

      tracker = {}
      for lg in left_group:
        tracker[lg.key] = lg.value
      for rg in right_group:
        lv = tracker.get(rg.key)
        if lv is not None:
          yield rg.key, (left_value_selector(lv), right_value_selector(rg.value))

    return partial_inner_join

  @staticmethod
  @comp_wrapper
  def tee(generator: Iterable[T]) -> Iterable[T]:
    '''itertools.tee - clone an iterable'''
    _, g = itertools.tee(iter(generator))
    return g
