import itertools
from composable import Composable
import shapeEval, functools, quicklog, collections.abc
from types import SimpleNamespace


f = Composable

class DictWrapper(dict):
  def __init__(self, d):
    #quicklog.log(f"__INIT__ dict wrapper: {type(d)} {dir(d)}")
    self.keys = d.keys() if isinstance(d, dict) else vars(d).keys()
    self.d = d

  def __getattr__(self, name):
    if name in self.keys:
      return self.d[name]
    return None

class KeyExistWrapper(dict):
  def __init__(self, d):
    self.keys = d.keys() if isinstance(d, dict) else vars(d).keys()

  def __getattr__(self, name):
    r = name in self.keys
    #quicklog.log(f"exists: {r}")
    return r

def normalize(obj):
  if isinstance(obj, dict): return DictWrapper(obj)
  if hasattr(obj, "__dict__"): return DictWrapper(vars(obj))
  return obj

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
      func(x)
  return partialForeach

def curriedFilter(func):
  def partialFilter(data):
    return filter(lambda x: func(normalize(x)), data)
  return partialFilter

def curriedReduce(func, initial=None):
  def partialReduce(data):
    return functools.reduce(func, data, initial)
  return partialReduce

def hasKey(key, obj):
  return key in vars(obj).keys()

def curriedFlatmap(func):
  def partialFlatmap(data):
    for ys in map(func, filter(lambda x: func(KeyExistWrapper(x)), data)):
      if not isinstance(ys, collections.abc.Iterable):
        #because either the field or it's container could be a collection
        ys = [ys]
      for y in ys:
        yield y
  return f(partialFlatmap)

def curriedAny(func):
  def curriedAny(data):
    return any(map(lambda x: func(normalize(x)), data))
  return curriedAny

def curriedAll(func):
  def curriedAll(data):
    return all(map(lambda x: func(normalize(x)), data))
  return curriedAll

def partialSort(data):
  return sorted(data)

def curriedSortby(func):
  def partialSortby(data):
    return sorted(data, key=func)
  return partialSortby

def curriedSortbyDescending(func):
  def partialSortbyDescending(data):
    return sorted(data, key=func, reverse=True)
  return partialSortbyDescending

def curriedTake(count):
  def partialTake(data):
    return data[0:count]
  return partialTake

def curriedGroup(func):
  def partialGroup(data):
    for key, value in itertools.groupby(sorted(data, key=func, reverse=True), key=func):
      yield SimpleNamespace(**{"key": key, "value": list(value)})
  return partialGroup

def curriedInnerJoin(leftData, leftKeyFunc, rightKeyFunc, leftValueSelector=None, rightValueSelector=None):
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
        #print(f"yield: {(rg.key, (leftValueSelector(lv), rightValueSelector(rg.value)))}")
        yield (rg.key, (leftValueSelector(lv), rightValueSelector(rg.value)))

  return f(partialInnerJoin)

def tee(generator):
  _, g = itertools.tee(iter(generator))
  return g

f.at = Composable(at)
f.map = Composable(curriedMap)
f.foreach = Composable(curriedForeach)
f.filter = Composable(curriedFilter)
f.reduce = Composable(curriedReduce)
f.list = Composable(list)
#f.distinct = Composable(lambda x: list(set(x))) #set does not work for complex types, should aggregate and compare
f.distinct = Composable(lambda x: list(functools.reduce(lambda a, b: a+[b] if b not in a else a, x, [])))
f.flatmap = Composable(curriedFlatmap)
f.shape = Composable(shapeEval.printShape)
f.shapeObj = Composable(shapeEval.evalShape)
f.any = Composable(curriedAny)
f.all = Composable(curriedAll)
f.reverse = Composable(reversed)
f.sort = Composable(partialSort)
f.sortBy = Composable(curriedSortby)
f.sortByDescending = Composable(curriedSortbyDescending)
f.take = Composable(curriedTake)
f.group = Composable(curriedGroup)
f.innerJoin = Composable(curriedInnerJoin)

f.tee = Composable(tee)