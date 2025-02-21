from .utility import normalize, ObjUtil
from .shape_eval import eval_shape, DictShape, ListShape, TupleShape, StrShape
from .composable import Composable
from typing import Callable, Any, Tuple, Iterable, Dict, Optional, Union, TypeVar
from types import SimpleNamespace
from .expression_builder import ExpressionExecutor
from .quicklog import log
import functools
import collections.abc
import itertools

f = Composable

def curried_at(func):
  def partial_at(obj):
    return func(normalize(obj))
  return f(partial_at)

def curried_select(func):
  exp = ExpressionExecutor(func)
  def partial_select(obj):
    return exp(normalize(obj))
  return f(partial_select)

def curried_map(func):
  def partial_map(data):
    return map(lambda x: func(normalize(x)), data)
  return f(partial_map)

def curried_foreach(func):
  def partial_foreach(data):
    for x in data:
      func(normalize(x))
  return f(partial_foreach)

def curried_filter(func):
  def partial_filter(data):
    return filter(lambda x: func(normalize(x)), data)
  return f(partial_filter)

def curried_reduce(func):
  def partial_reduce(data):
    return functools.reduce(func, data)
  return f(partial_reduce)

def curried_reduce2(func, initial):
  def partial_reduce(data):
    return functools.reduce(func, data, initial)
  return f(partial_reduce)

def curried_flatmap(func):
  def partial_flatmap(data):
    for ys in map(lambda x: func(normalize(x)), data):
      for y in ys:
        yield y
  return f(partial_flatmap)

def curried_any(func):
  def curried_any(data):
    return any(map(lambda x: func(normalize(x)), data))
  return f(curried_any)

def curried_all(func):
  def partial_all(data):
    return all(map(lambda x: func(normalize(x)), data))
  return f(partial_all)

def partial_sort(data):
  return sorted(ObjUtil.exec_generator(data))

def curried_sortby(func):
  def partial_sortby(data):
    return sorted(ObjUtil.exec_generator(data), key=func)
  return f(partial_sortby)

def curried_sortby_descending(func):
  def partial_sortby_descending(data):
    return sorted(ObjUtil.exec_generator(data), key=func, reverse=True)
  return f(partial_sortby_descending)

def curried_take(count):
  def partial_take(data):
    iter_count = 0
    for x in data:
      iter_count += 1
      if iter_count > count:
        break
      yield x
  return f(partial_take)

def curried_skip(skip_count):
  def partial_skip(data):
    iter_count = 0
    for x in data:
      iter_count += 1
      if iter_count > skip_count:
        yield x
  return f(partial_skip)

def curried_group(func):
  def partial_group(data):
    for key, value in itertools.groupby(sorted(ObjUtil.exec_generator(data), key=func, reverse=True), key=func):
      yield SimpleNamespace(**{"key": key, "value": ObjUtil.exec_generator(value)})
  return f(partial_group)

def curried_inner_join(left_data, left_key_func, right_key_func, left_value_selector=None, right_value_selector=None):
  if left_value_selector is None: left_value_selector = lambda x: x
  if right_value_selector is None: right_value_selector = lambda x: x

  def partial_inner_join(right_data):
    left_group = curried_group(left_key_func)(left_data)
    right_group = curried_group(right_key_func)(right_data)

    tracker = {}
    for lg in left_group:
      tracker[lg.key] = lg.value
    for rg in right_group:
      lv = tracker.get(rg.key)
      if lv is not None:
        yield rg.key, (left_value_selector(lv), right_value_selector(rg.value))

  return f(partial_inner_join)

def tee(generator):
  _, g = itertools.tee(iter(generator))
  return g


type T = TypeVar('T')
type T2 = TypeVar('T2')
type R = TypeVar('R')
type L = TypeVar('L')
type K = TypeVar('K')

type PropertySelector = Callable[[T], R]
type KeySelector = Callable[[T], K]

class Api:

  @staticmethod
  #def at(func:PropertySelector) -> Callable[[T], R]:
  def at(func):
    '''property selector'''
    pass

  @staticmethod
  #def select(func:PropertySelector) -> Callable[[T], R]:
  def select(func):
    '''like map with chainable property selection'''
    pass

  @staticmethod
  #def map(func:PropertySelector) -> Callable[[Iterable[T]], Iterable[R]]:
  def map(func):
    '''curried version of python's map:
    map(func, *iterables) --> map object\n\nMake an iterator that computes the function using arguments from\neach of the iterables.  Stops when the shortest iterable is exhausted.
    '''
    pass

  @staticmethod
  #def foreach(func:PropertySelector) -> Callable[[Iterable[T]], Any]: pass
  def foreach(func): pass

  @staticmethod
  #def filter(func:PropertySelector) -> Callable[[Iterable[T]], Iterable[R]]:
  def filter(func):
    '''curried version of python's filter
    filter(function or None, iterable) --> filter object\n\nReturn an iterator yielding those items of iterable for which function(item)\nis true. If function is None, return the items that are true.
    '''
    pass

  @staticmethod
  #def reduce(func:Callable[[T, T], R]) -> Callable[[T], R]:
  def reduce(func):
    '''curried version of functools's reduce (to use initial value, use reduce2)
    reduce(function, iterable) -> value\n\nApply a function of two arguments cumulatively to the items of an iterable, from left to right.\n\nThis effectively reduces the iterable to a single value.  If initial is present,\nit is placed before the items of the iterable in the calculation, and serves as\na default when the iterable is empty.\n\nFor example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])\ncalculates ((((1 + 2) + 3) + 4) + 5).
    '''
    pass

  @staticmethod
  #def reduce2(func:Callable[[T, T, R], R]) -> Callable[[T], R]:
  def reduce2(func):
    '''curried version of functools's reduce
    reduce(function, iterable, initial) -> value\n\nApply a function of two arguments cumulatively to the items of an iterable, from left to right.\n\nThis effectively reduces the iterable to a single value.  If initial is present,\nit is placed before the items of the iterable in the calculation, and serves as\na default when the iterable is empty.\n\nFor example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])\ncalculates ((((1 + 2) + 3) + 4) + 5).
    '''
    pass

  @staticmethod
  #def list(func: Iterable[T]) -> list[R]:
  def list(func):
    '''curried version of python's list
    Built-in mutable sequence.\n\nIf no argument is given, the constructor creates a new empty list.\nThe argument must be an iterable if specified.
    '''
    pass

  @staticmethod
  #def distinct(func:Callable[[T], Iterable[R]]) -> Callable[[T], Iterable[R]]:
  def distinct(func):
    '''a general purpose distinct implementation where performance is not required
    if your data is compatible, you may be able to use distinctSet
    '''
    pass

  @staticmethod
  #def distinct_set(func:Callable[[T], Iterable[R]]) -> Callable[[T], Iterable[R]]:
  def distinct_set(func):
    '''implementation of distinct using python's set, but limited to qualifying primitive types'''
    pass

  @staticmethod
  #def flatmap(func:Callable[[T], Iterable[Iterable[R]]]) -> Callable[[T], Iterable[R]]:
  def flatmap(func):
    '''iterable implementation of flatmap using python's native map'''
    pass

  @staticmethod
  #def flatmap(func:Callable[[T], Iterable[Iterable[R]]]) -> Callable[[T], Iterable[R]]:
  def flatmapid(func):
    '''iterable implementation of flatmap using python's native map'''
    pass

  @staticmethod
  #def shape(obj:T) -> Union[DictShape|ListShape|TupleShape|StrShape]:
  def shape(obj):
    '''evaluates the shape of data, returns a shape object, pprints thru __repr__'''
    pass

  @staticmethod
  #def any(func:Callable[[T], bool]) -> Callable[[Iterable[T]], bool]: pass
  def any(func): pass

  @staticmethod
  #def all(func:Callable[[T], bool]) -> Callable[[Iterable[T]], bool]: pass
  def all(func): pass

  @staticmethod
  #def reverse(data:Iterable[T]) -> Iterable[R]:
  def reverse(data):
    '''curried version of python's reverse'''
    pass

  @staticmethod
  #def sort(data:Iterable[T]) -> Iterable[R]:
  def sort(data):
    '''curried version of python's sort'''
    pass

  @staticmethod
  #def sort_by(func:PropertySelector) -> Callable[[Iterable[T]], Iterable[R]]:
  def sort_by(func):
    '''curried version of python's sort with key selector'''
    pass

  @staticmethod
  #def sort_by_descending(func:PropertySelector) -> Callable[[Iterable[T]], Iterable[R]]:
  def sort_by_descending(func):
    '''curried version of python's sort w/ key selector followed by reverse'''
    pass

  @staticmethod
  #def take(count:int) -> Callable[[Iterable[T]], Iterable[R]]:
  def take(count):
    '''basically list[0:count]'''
    pass

  @staticmethod
  #def skip(count:int) -> Callable[[Iterable[T]], Iterable[R]]:
  def skip(count):
    '''basically list[count:]'''
    pass

  @staticmethod
  #def group(func:PropertySelector) -> Callable[[Iterable[T]], Iterable[Dict[T, Iterable[R]]]]:
  def group(func):
    '''curried version of itertools.groupby
    sort by key is used before grouping to achieve singular grouping
    f.groupby(lambda x.property)
    this implementation runs the iterable for the grouping, but yields the key/value pair as a new iterable
    '''
    pass

  @staticmethod
  #def inner_join(left_data:T, left_key_selector:KeySelector, right_keySelector:KeySelector, left_dataSelector:PropertySelector, right_dataSelector:PropertySelector) -> Callable[[T2], Iterable[Tuple[K, Tuple[T, T2]]]]:
  def inner_join(left_data, left_key_selector, right_key_selector, left_data_selector, right_data_selector):
    '''combine two groups by key
    f.innerJoin(left_data, left_keySelector, right_keySelector, left_dataSelector, right_dataSelector)
    returns a tuple of (key, (left_data, right_data))
    '''
    pass

  @staticmethod
  #def tee(gen:Iterable) -> Iterable:
  def tee(gen):
    '''itertools.tee - clone an iterable'''
    pass
#
# def getExtDoc():
#   api = list(map(lambda x: getattr(Api, x), filter(lambda x: "__" not in x, dir(Api))))
#   return [(x.__name__, x.__doc__, x.__annotations__) for x in api]
#
# extDoc = getExtDoc()

Api = f
Api.at = Composable(curried_at)
Api.select = Composable(curried_select)
Api.map = Composable(curried_map)
Api.foreach = Composable(curried_foreach)
Api.filter = Composable(curried_filter)
Api.reduce = Composable(curried_reduce)
Api.reduce2 = Composable(curried_reduce2)
Api.list = Composable(list)
Api.distinct = Composable(lambda x: list(functools.reduce(lambda a, b: a+[b] if b not in a else a, x, [])))
Api.distinct_set = Composable(lambda x: list(set(x)))
Api.flatmap = Composable(curried_flatmap)
Api.flatmapid = Composable(curried_flatmap)(lambda x: x)
Api.shape = Composable(eval_shape)
Api.any = Composable(curried_any)
Api.all = Composable(curried_all)
Api.reverse = Composable(lambda x: reversed(ObjUtil.exec_generator(x)))
Api.sort = Composable(partial_sort)
Api.sort_by = Composable(curried_sortby)
Api.sort_by_descending = Composable(curried_sortby_descending)
Api.take = Composable(curried_take)
Api.skip = Composable(curried_skip)
Api.group = Composable(curried_group)
Api.inner_join = Composable(curried_inner_join)
Api.tee = Composable(tee)
#
# def updateExtDoc(doc):
#   # (name, doc, annotations)
#   for ed in doc:
#     attr = getattr(f, ed[0])
#     setattr(attr, '__doc__', ed[1] or "undocumented")
#     setattr(attr, '__annotations__', ed[2])
#
# updateExtDoc(extDoc)
#
