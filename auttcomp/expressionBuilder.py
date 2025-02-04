from .quicklog import log
from typing import Iterable

printTracking = True

class Ghost(object):
  def __init__(self):
    super().__init__()
    self.tracking = []

  def __getattr__(self, name):
    self.tracking.append(name)
    return self

#in this domain, everything is considered a list
class ExpressionExecutor:
  def __init__(self, func):
    self.__func = func

  @staticmethod
  def recursiveEval(tracking, obj):
    if len(tracking) == 0: return obj
    prop = tracking.pop()
    if isinstance(obj, list):
      pass

  def __call__(self, data):
    g = Ghost()
    r = self.__func(g)
    evalResult = ExpressionExecutor.recursiveEval(list(reversed(r.tracking)), data)
    if not isinstance(evalResult, Iterable): return [evalResult]
    return evalResult
