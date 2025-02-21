from types import SimpleNamespace
from typing import Iterable

#NOTE - experimental work in progress

class Ghost:
  def __init__(self):
    self.tracking = []

  def __getattr__(self, name):
    self.tracking.append(name)
    return self

#in this domain, everything is considered a list
class ExpressionExecutor:
  def __init__(self, func):
    self.__func = func

  @staticmethod
  def recursive_eval(tracking, obj):
    if len(tracking) == 0: return obj
    prop = tracking.pop()
    if isinstance(obj, list):
      return ExpressionExecutor.recursive_eval(tracking, list(map(lambda x: getattr(x, prop), obj)))
    if isinstance(obj, dict):
      return ExpressionExecutor.recursive_eval(tracking, obj[prop])
    if isinstance(obj, SimpleNamespace):
      return ExpressionExecutor.recursive_eval(tracking, getattr(obj, prop))
    raise Exception(f"unexpected flow {type(obj)}")

  def __call__(self, data):
    g = Ghost()
    r = self.__func(g)
    eval_result = ExpressionExecutor.recursive_eval(list(reversed(r.tracking)), data)
    if not isinstance(eval_result, Iterable): return [eval_result]
    return eval_result
