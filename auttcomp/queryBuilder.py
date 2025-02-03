from collections.abc import Callable
from .shapeEval import evalShape
from .quicklog import log

import sys

printTracking = True

class Ghost(object):
  def __init__(self, id=1):
    super().__init__()
    self.tracking = []
    self.id = id

  def __repr__(self):
    return "****SELF****"



  def __getattr__(self, name):
    if printTracking: print(f"{self.id} __getattr__ {name}")
    self.tracking.append([name])
    if printTracking: print(self.tracking)
    return self

  def __getitem__(self, index):
    if printTracking: print(f"{self.id} __getitem__ {index}")
    self.tracking.append(index.tracking)
    return None




  def __index__(self):
    print("index")

  def __bool__(self):
    print(f"__bool__")
    return True
    raise Exception("invalid operation - not allowed to return anything other than bool")

  def __iter__(self):
    print('iter')

  def __contains__(self, item):
    print(f"__contains__ {item}")
    #raise Exception("invalid operation - requires bool return")

    return True

  def __call__(self, *args, **kwargs):
    print(f"__call__ {args}")
    return self.tracking



  def __eq__(self, other):
    print(f"__eq__ {('==', other)}")
    self.tracking[-1:][0].append(('==', other))
    return other

  def __ne__(self, other):
    print(f"__ne__ {('!=', other)}")
    self.tracking[-1:][0].append(('!=', other))
    return other

  def __and__(self, other):
    print(f"__and__ {other}")
    self.tracking.append(('and', other(self.tracking)))
    return other

  def __or__(self, other):
    print(f"__or__ {other}")
    self.tracking.append(('or', other(self.tracking)))
    return other

  def __gt__(self, other):
    print(f"__gt__ {other}")
    self.tracking[-1:][0].append(('>', other))
    return other

  def __lt__(self, other):
    print(f"__lt__ {other}")
    self.tracking[-1:][0].append(('<', other))
    return other

  def __add__(self, other):
    print(f"__add__ {other}")
    self.tracking.append(('add', other(self.tracking)))
    return other

  #def __rshift__(self, other):


def select(func):
  g = Ghost()
  r = func(g)
  return r.tracking