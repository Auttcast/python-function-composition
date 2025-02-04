from .utility import normalize, normalizeForKeyExists
from .shapeEval import evalShape, DictShape, ListShape, TupleShape, StrShape
from .composable import Composable
from typing import Callable, Any, Tuple, Iterable, Dict, Optional, Union
from types import SimpleNamespace
import functools, collections.abc, itertools

f = Composable

def at(func):
  def atPart(obj):
      return func(normalize(obj))
  return f(atPart)

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
    for ys in map(func, filter(lambda x: func(normalizeForKeyExists(x)), data)):
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
  return sorted(data)

def curriedSortby(func):
  def partialSortby(data):
    return sorted(data, key=func)
  return f(partialSortby)

def curriedSortbyDescending(func):
  def partialSortbyDescending(data):
    return sorted(data, key=func, reverse=True)
  return f(partialSortbyDescending)

def curriedTake(count):
  def partialTake(data):
    return data[0:count]
  return f(partialTake)

def curriedSkip(count):
  def partialSkip(data):
    return data[count:]
  return f(partialSkip)

def curriedGroup(func):
  def partialGroup(data):
    for key, value in itertools.groupby(sorted(data, key=func, reverse=True), key=func):
      yield SimpleNamespace(**{"key": key, "value": list(value)})
  return f(partialGroup)

def curriedInnerJoin(leftData, leftKeyFunc, rightKeyFunc, leftValueSelector, rightValueSelector):
  if leftValueSelector is None: leftValueSelector = lambda x: x
  if rightValueSelector is None: rightValueSelector = lambda x: x
  def partialInnerJoin(rightData):
    leftGroup = curriedGroup(leftKeyFunc)(leftData)
    rightGroup = curriedGroup(rightKeyFunc)(rightData)

    tracker = {}
    for lg in leftGroup:
      tracker[lg.key] = lg.value
    for rg in rightGroup:
      lv = tracker.get(rg.key)
      if lv is not None:
        yield (rg.key, (leftValueSelector(lv), rightValueSelector(rg.value)))

  return f(partialInnerJoin)

def tee(generator):
  _, g = itertools.tee(iter(generator))
  return g

class Api:

  @staticmethod
  def at(func:Callable[[Any], Any]) -> Callable[[Any], Any]:
    '''property selector'''
    pass

  @staticmethod
  def map(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''curried version of python's map:
    map(func, *iterables) --> map object\n\nMake an iterator that computes the function using arguments from\neach of the iterables.  Stops when the shortest iterable is exhausted.
    '''
    pass

  @staticmethod
  def foreach(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Any]: pass

  @staticmethod
  def filter(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''curried version of python's filter
    filter(function or None, iterable) --> filter object\n\nReturn an iterator yielding those items of iterable for which function(item)\nis true. If function is None, return the items that are true.
    '''
    pass

  @staticmethod
  def reduce(func:Callable[[Any, Any], Any]) -> Callable[[Any], Any]:
    '''curried version of functools's reduce (to use initial value, use reduce2)
    reduce(function, iterable) -> value\n\nApply a function of two arguments cumulatively to the items of an iterable, from left to right.\n\nThis effectively reduces the iterable to a single value.  If initial is present,\nit is placed before the items of the iterable in the calculation, and serves as\na default when the iterable is empty.\n\nFor example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])\ncalculates ((((1 + 2) + 3) + 4) + 5).
    '''
    pass

  @staticmethod
  def reduce2(func:Callable[[Any, Any, Any], Any]) -> Callable[[Any], Any]:
    '''curried version of functools's reduce
    reduce(function, iterable, initial) -> value\n\nApply a function of two arguments cumulatively to the items of an iterable, from left to right.\n\nThis effectively reduces the iterable to a single value.  If initial is present,\nit is placed before the items of the iterable in the calculation, and serves as\na default when the iterable is empty.\n\nFor example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])\ncalculates ((((1 + 2) + 3) + 4) + 5).
    '''
    pass

  @staticmethod
  def list(func: Iterable[Any]) -> list[Any]:
    '''curried version of python's list
    Built-in mutable sequence.\n\nIf no argument is given, the constructor creates a new empty list.\nThe argument must be an iterable if specified.
    '''
    pass

  @staticmethod
  def distinct(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''a general purpose distinct implementation where performance is not required
    if your data is compatible, you may be able to use distinctSet
    '''
    pass

  @staticmethod
  def distinctSet(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''implementation of distinct using python's set, but limited to qualifying primitive types'''
    pass

  @staticmethod
  def flatmap(func:Callable[[Any], Iterable[Iterable[Any]]]) -> Callable[[Any], Iterable[Any]]:
    '''iterable implementation of flatmap using python's native map'''
    pass

  @staticmethod
  def shape(obj:Any) -> Union[DictShape|ListShape|TupleShape|StrShape]:
    '''evaluates the shape of data, returns a shape object, pprints thru __repr__'''
    pass

  @staticmethod
  def any(func:Callable[[Any], Iterable[Any]]) -> bool: pass

  @staticmethod
  def all(func:Callable[[Any], Iterable[Any]]) -> bool: pass

  @staticmethod
  def reverse(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''curried version of python's reverse'''
    pass

  @staticmethod
  def sort(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''curried version of python's sort'''
    pass

  @staticmethod
  def sortBy(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''curried version of python's sort with key selector'''
    pass

  @staticmethod
  def sortByDescending(func:Callable[[Any], Iterable[Any]]) -> Callable[[Any], Iterable[Any]]:
    '''curried version of python's sort w/ key selector followed by reverse'''
    pass

  @staticmethod
  def take(count:int) -> Callable[[Any], Iterable[Any]]:
    '''basically list[0:count]'''
    pass

  @staticmethod
  def skip(count:int) -> Callable[[Any], Any]:
    '''basically list[count:]'''
    pass

  @staticmethod
  def group(func:Callable[[Any], Any]) -> Callable[[Any], Iterable[Dict[Any, Iterable[Any]]]]:
    '''curried version of itertools.groupby
    f.groupby(lambda x.property)
    this implementation runs the iterable for the grouping, but yields the key/value pair as a new iterable
    '''
    pass

  @staticmethod
  def innerJoin(leftData:Any, leftKeySelector:Callable[[Any], Any], rightKeySelector:Callable[[Any], Any], leftDataSelector:Callable[[Any], Any], rightDataSelector:Callable[[Any], Any]) -> Callable[[Any], Iterable[Tuple[Any, Any]]]:
    '''combine two groups by key
    f.innerJoin(leftData, leftKeySelector, rightKeySelector, leftDataSelector, rightDataSelector)
    returns a tuple of (key, (leftData, rightData))
    '''
    pass

  @staticmethod
  def tee(gen:Iterable) -> Iterable:
    '''itertools.tee - clone an iterable'''
    pass

def getExtDoc():
  api = list(map(lambda x: getattr(Api, x), filter(lambda x: "__" not in x, dir(Api))))
  return [(x.__name__, x.__doc__, x.__annotations__) for x in api]

extDoc = getExtDoc()

Api = f
Api.at = Composable(at)
Api.map = Composable(curriedMap)
Api.foreach = Composable(curriedForeach)
Api.filter = Composable(curriedFilter)
Api.reduce = Composable(curriedReduce)
Api.reduce2 = Composable(curriedReduce2)
Api.list = Composable(list)
Api.distinct = Composable(lambda x: list(functools.reduce(lambda a, b: a+[b] if b not in a else a, x, [])))
Api.distinctSet = Composable(lambda x: list(set(x)))
Api.flatmap = Composable(curriedFlatmap)
Api.shape = Composable(evalShape)
Api.any = Composable(curriedAny)
Api.all = Composable(curriedAll)
Api.reverse = Composable(reversed)
Api.sort = Composable(partialSort)
Api.sortBy = Composable(curriedSortby)
Api.sortByDescending = Composable(curriedSortbyDescending)
Api.take = Composable(curriedTake)
Api.skip = Composable(curriedSkip)
Api.group = Composable(curriedGroup)
Api.innerJoin = Composable(curriedInnerJoin)
Api.tee = Composable(tee)

def updateExtDoc(doc):
  # (name, doc, annotations)
  for ed in doc:
    attr = getattr(f, ed[0])
    setattr(attr, '__doc__', ed[1] or "undocumented")
    setattr(attr, '__annotations__', ed[2])

updateExtDoc(extDoc)

