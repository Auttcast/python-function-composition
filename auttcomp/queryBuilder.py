from collections.abc import Callable
from types import SimpleNamespace

from .shapeEval import evalShape
from .quicklog import log





class Ghost(object):
  def __init__(self, tracking=None):
    super().__init__()

    if tracking is None:
      self.tracking = OwnedList(self)
    else:
      self.tracking = tracking

  def logPropAccess(self, message):
    if True:
      log(message)
  #
  # def __getattribute__(self, item):
  #   print(f"__getattribute__ {item}")
  #   #log(f"__getattr__ {self.tracking} {item}")
  #   log(f"__getattribute__ {self == self} {item}")
  #   #self.tracking.append(item)
  #   return self.tracking

  def __getattr__(self, name):
    return Ghost(self.tracking + [name])

  def __setattr__(self, key, value):
    print(f"SET:::::: {key} value: {value} inst: {type(value)}")
    if isinstance(value, Ghost): return
    super().__setattr__(key, value)

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
    if index == self: return self
    self.logPropAccess(f"__gt__ {self.tracking} {index}")
    shape = Ghost.__prepareAndEval(index)
    print(f"SHAPE:::: {shape}")

    if isinstance(index, Ghost): # [x.foo == "bar"]
      shapes = [
        ['Any', ('Any',)],
        ({'tracking': ['Any', ('Any',)]},)
      ]

      self.tracking.append([index[x].tracking[0] for x in range(0, len(index))])
    elif isinstance(index, Callable): # [lambda x.foo == "bar"]
      self.tracking.append(index(Ghost()).tracking)

    else: # [x.foo, x.bar, x.baz]
      shapes = [
        ({'tracking': ['Any']},)
      ]

      self.tracking.append([index[x].tracking[0] for x in range(0, len(index))])
    return self

  def __gt__(self, other):
    self.logPropAccess(f"__gt__ {self.tracking} {other}")
    self.tracking.append(('>', other))
    return self

  def __lt__(self, other):
    self.logPropAccess(f"__lt__ {self.tracking} {other}")
    self.tracking.append(('<', other))
    return self

  def __eq__(self, other):
    self.logPropAccess(f"__eq__ {self.tracking} {other}")
    self.tracking.append(('==', other))
    return self

  def __and__(self, other):
    self.logPropAccess(f"__and__ {self.tracking} {other}")
    self.tracking.append(('and', other(self.tracking)))
    #join?
    return self

  def __bool__(self):
    raise Exception("invalid operation - not allowed to return anything other than bool")

  def __call__(self, *args, **kwargs):
    return self.tracking

  def __or__(self, other):
    self.logPropAccess(f"__or__ {self.tracking} {other}")
    self.tracking.append(('or', other))
    #composition or filtering
    return self

  def __contains__(self, item):
    raise Exception("invalid operation - requires bool return")

  def __add__(self, other):
    self.logPropAccess(f"__add__ {self.tracking} {other}")
    self.tracking.append(('add', other(self.tracking)))
    return self
