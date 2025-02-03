from collections.abc import Callable
from .shapeEval import evalShape
from .quicklog import log

class Ghost(object):
  def __init__(self):
    super().__init__()
    self.tracking = []

  def __repr__(self):
    return "****SELF****"

  def __getattr__(self, name):
    print(f"__getattr__ {name}")
    self.tracking.append([name])
    return self

  def __getitem__(self, index):
    print(f"__getitem__ {index}")
    return self

  def __gt__(self, other):
    print(f"__gt__ {other}")
    self.tracking.append(('>', other))
    return self

  def __lt__(self, other):
    print(f"__lt__ {other}")
    self.tracking.append(('<', other))
    return self

  def __index__(self):
    print("index")

  def __eq__(self, other):
    print(f"__eq__ {('==', other)}")
    self.tracking.append(('==', other))
    return other

  def __and__(self, other):
    print(f"__and__ {other}")
    self.tracking.append(('and', other(self.tracking)))
    return self

  def __bool__(self):
    print(f"__bool__")
    raise Exception("invalid operation - not allowed to return anything other than bool")

  def __call__(self, *args, **kwargs):
    print(f"__call__")
    return self.tracking

  def __or__(self, other):
    print(f"__or__ {other}")
    self.tracking.append(('or', other))
    return self

  def __contains__(self, item):
    print(f"__contains__ {item}")
    raise Exception("invalid operation - requires bool return")

  def __add__(self, other):
    print(f"__add__ {other}")
    self.tracking.append(('add', other(self.tracking)))
    return self

  #def __rshift__(self, other):
