from .utility import normalize, ObjUtil
from .shapeEval import evalShape, DictShape, ListShape, TupleShape, StrShape
from .composable import Composable
from typing import Callable, Any, Tuple, Iterable, Dict, Optional, Union, TypeVar
from types import SimpleNamespace
import functools, collections.abc, itertools
from .expressionBuilder import ExpressionExecutor
from .quicklog import log

f = Composable

def at(func):
  def atPart(obj):
      return func(normalize(obj))
  return f(atPart)

def curriedSelect(func):
  exp = ExpressionExecutor(func)
  def partialSelect(obj):
    return exp(normalize(obj))
  return f(partialSelect)

def curriedMap(func):
  def partialMap(data):
    return map(lambda x: func(normalize(x)), data)
  return f(partialMap)

def curriedForeach(func):
  def partialForeach(data):
    for x in data:
      func(normalize(x))
  return f(partialForeach)

def curriedFilter(func):
  def partialFilter(data):
    return filter(lambda x: func(normalize(x)), data)
  return f(partialFilter)

def curriedReduce(func):
  def partialReduce(data):
    return functools.reduce(func, data)
  return f(partialReduce)

def curriedReduce2(func, initial):
  def partialReduce(data):
    return functools.reduce(func, data, initial)
  return f(partialReduce)

def hasKey(key, obj):
  return key in vars(obj).keys()

def curriedFlatmap(func):
  def partialFlatmap(data):
    for ys in map(func, filter(lambda x: func(normalize(x)), data)):
      if not isinstance(ys, collections.abc.Iterable):
        #because either the field or it's container could be a collection
        ys = [ys]
      for y in ys:
        yield y
  return f(partialFlatmap)

def curriedAny(func):
  def curriedAny(data):
    return any(map(lambda x: func(normalize(x)), data))
  return f(curriedAny)

def curriedAll(func):
  def curriedAll(data):
    return all(map(lambda x: func(normalize(x)), data))
  return f(curriedAll)

def partialSort(data):
  return sorted(ObjUtil.execGenerator(data))

def curriedSortby(func):
  def partialSortby(data):
    return sorted(ObjUtil.execGenerator(data), key=func)
  return f(partialSortby)

def curriedSortbyDescending(func):
  def partialSortbyDescending(data):
    return sorted(ObjUtil.execGenerator(data), key=func, reverse=True)
  return f(partialSortbyDescending)

def curriedTake(count):
  def partialTake(data):
    for i in range(0, count):
      yield data[i]
  return f(partialTake)

def curriedSkip(skipCount):
  def partialSkip(data):
    c = 0
    for i in data:
      c += 1
      if c > skipCount:
        yield data[c-1]
  return f(partialSkip)

def curriedGroup(func):
  def partialGroup(data):
    for key, value in itertools.groupby(sorted(ObjUtil.execGenerator(data), key=func, reverse=True), key=func):
      yield SimpleNamespace(**{"key": key, "value": ObjUtil.execGenerator(value)})
  return f(partialGroup)

def curriedInnerJoin(leftData, leftKeyFunc, rightKeyFunc, valueSelector):
  if valueSelector is None: valueSelector = lambda x: x

  def partialInnerJoin(rightData):
    leftGroup = curriedGroup(leftKeyFunc)(leftData)
    rightGroup = curriedGroup(rightKeyFunc)(rightData)

    tracker = {}
    for lg in leftGroup:
      tracker[lg.key] = lg.value
    for rg in rightGroup:
      lv = tracker.get(rg.key)
      if lv is not None:
        yield (rg.key, valueSelector(lv, rg.value))

  return f(partialInnerJoin)

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
  #def distinctSet(func:Callable[[T], Iterable[R]]) -> Callable[[T], Iterable[R]]:
  def distinctSet(func):
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
  #def sortBy(func:PropertySelector) -> Callable[[Iterable[T]], Iterable[R]]:
  def sortBy(func):
    '''curried version of python's sort with key selector'''
    pass

  @staticmethod
  #def sortByDescending(func:PropertySelector) -> Callable[[Iterable[T]], Iterable[R]]:
  def sortByDescending(func):
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
  #def innerJoin(leftData:T, leftKeySelector:KeySelector, rightKeySelector:KeySelector, leftDataSelector:PropertySelector, rightDataSelector:PropertySelector) -> Callable[[T2], Iterable[Tuple[K, Tuple[T, T2]]]]:
  def innerJoin(leftData, leftKeySelector, rightKeySelector, leftDataSelector, rightDataSelector):
    '''combine two groups by key
    f.innerJoin(leftData, leftKeySelector, rightKeySelector, leftDataSelector, rightDataSelector)
    returns a tuple of (key, (leftData, rightData))
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
Api.at = Composable(at)
Api.select = Composable(curriedSelect)
Api.map = Composable(curriedMap)
Api.foreach = Composable(curriedForeach)
Api.filter = Composable(curriedFilter)
Api.reduce = Composable(curriedReduce)
Api.reduce2 = Composable(curriedReduce2)
Api.list = Composable(list)
Api.distinct = Composable(lambda x: list(functools.reduce(lambda a, b: a+[b] if b not in a else a, x, [])))
Api.distinctSet = Composable(lambda x: list(set(x)))
Api.flatmap = Composable(curriedFlatmap)
Api.flatmapid = Composable(curriedFlatmap(lambda x: x))
Api.shape = Composable(evalShape)
Api.any = Composable(curriedAny)
Api.all = Composable(curriedAll)
Api.reverse = Composable(lambda x: reversed(ObjUtil.execGenerator(x)))
Api.sort = Composable(partialSort)
Api.sortBy = Composable(curriedSortby)
Api.sortByDescending = Composable(curriedSortbyDescending)
Api.take = Composable(curriedTake)
Api.skip = Composable(curriedSkip)
Api.group = Composable(curriedGroup)
Api.innerJoin = Composable(curriedInnerJoin)
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
