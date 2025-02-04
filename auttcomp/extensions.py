from .utility import normalize, normalizeForKeyExists
from .shapeEval import evalShape, printShape
from .composable import Composable
from typing import Callable, Any, Tuple, Iterable, Dict, Optional
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
  def at(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def map(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def foreach(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def filter(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def reduce(func:Callable[[Any, Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def reduce2(func:Callable[[Any, Any, Optional[Any]], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def list(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def distinct(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def flatmap(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def shape(obj:Any) -> (): pass

  @staticmethod
  def any(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def all(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def reverse(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def sort(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def sortBy(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def sortByDescending(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

  @staticmethod
  def take(count:int) -> Callable[[Any], Any]: pass

  @staticmethod
  def skip(count:int) -> Callable[[Any], Any]: pass

  @staticmethod
  def group(func:Callable[[Any], Any]) -> Callable[[Any], Iterable[Dict[Any, Iterable[Any]]]]: pass

  @staticmethod
  def innerJoin(leftData:Any, leftKeySelector:Callable[[Any], Any], rightKeySelector:Callable[[Any], Any], leftDataSelector:Callable[[Any], Any], rightDataSelector:Callable[[Any], Any]) -> Callable[[Any], Iterable[Tuple[Any, Any]]]: pass

  @staticmethod
  def tee(func:Callable[[Any], Any]) -> Callable[[Any], Any]: pass

Api = f

Api.at = Composable(at)
Api.map = Composable(curriedMap)
Api.foreach = Composable(curriedForeach)
Api.filter = Composable(curriedFilter)
Api.reduce = Composable(curriedReduce)
Api.reduce2 = Composable(curriedReduce2)
Api.list = Composable(list)
Api.distinct = Composable(lambda x: list(functools.reduce(lambda a, b: a+[b] if b not in a else a, x, [])))
Api.flatmap = Composable(curriedFlatmap)
Api.shape = Composable(printShape)
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
