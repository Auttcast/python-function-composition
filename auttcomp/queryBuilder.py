from collections.abc import Callable
from .quicklog import *
from .shapeEval import evalShape

class Ghost():
  def __init__(self, tracking=[]):
    self.tracking = tracking

  def __getattr__(self, name):
    return Ghost(self.tracking + [name])

  @staticmethod
  def __getRootContainer(obj, parent=None):
    if isinstance(obj, Ghost): return type(parent) if parent is not None else None
    if not isinstance(obj, Ghost): return Ghost.__getRootContainer(obj[0], obj)

  @staticmethod
  def __prepareAndEval(obj):
    if isinstance(obj, Ghost):
      return evalShape(obj.tracking, setAnyType=True)
    else:
      return evalShape(obj, setAnyType=True)

  def __getitem__(self, index):
    #targetType = self.__getRootContainer()

    log(f"!!!!!!!!index.tracking: len:{Ghost.__prepareAndEval(index)}")
    if isinstance(index, Ghost):
      # [x.foo == "bar"]
      log(f"expression {index.tracking}")

      self.tracking.append([index[x].tracking[0] for x in range(0, len(index))])

    elif isinstance(index, Callable):
      # [lambda x.foo == "bar"]
      log(f"lambda {index.tracking}")

      self.tracking.append(index(Ghost()).tracking)

    else:
      # [x.foo] 1 tuple???
      # [x.foo, x.bar, x.baz]
      log(f"tuple {index}")

      self.tracking.append([index[x].tracking[0] for x in range(0, len(index))])

    return self

  def __gt__(self, other):
    self.tracking.append(('>', other))
    return self

  def __lt__(self, other):
    self.tracking.append(('<', other))
    return self

  def __eq__(self, other):
    self.tracking.append(('==', other))
    return self

  def __and__(self, other):
    self.tracking.append(('and', other(self.tracking)))
    #join?
    return self

  def __bool__(self):
    raise Exception("invalid operation - not allowed to return anything other than bool")

  def __call__(self, *args, **kwargs):
    return self.tracking

  def __or__(self, other):
    self.tracking.append(('or', other))
    #composition or filtering
    return self

  def __contains__(self, item):
    raise Exception("invalid operation - requires bool return")

  def __add__(self, other):
    self.tracking.append(('add', other(self.tracking)))
    return self
