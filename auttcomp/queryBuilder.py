from .quicklog import log

printTracking = True

class Ghost(object):
  def __init__(self, id=1):
    super().__init__()
    self.tracking = []
    self.id = id

  def __repr__(self):
    return "****SELF****"



  def __getattr__(self, name):
    if printTracking: log(f"{self.id} __getattr__ {name}")
    self.tracking.append([name])
    if printTracking: log(self.tracking)
    return self

  def __getitem__(self, index):
    if printTracking: log(f"{self.id} __getitem__ {index}")
    self.tracking.append(index.tracking)
    return None




  def __index__(self):
    log("index")

  def __bool__(self):
    log(f"__bool__")
    raise Exception("invalid expression: use == True|False instead")

  def __iter__(self):
    log('iter')

  def __contains__(self, item):
    log(f"__contains__ {item}")
    #raise Exception("invalid operation - requires bool return")
    return True

  def __call__(self, *args, **kwargs):
    log(f"__call__ {args}")
    return self



  def __eq__(self, other):
    log(f"__eq__ {('==', other)}")
    self.tracking[-1:][0].append(('==', other))
    return other

  def __ne__(self, other):
    log(f"__ne__ {('!=', other)}")
    self.tracking[-1:][0].append(('!=', other))
    return other

  def __and__(self, other):
    log(f"__and__ {other}")
    self.tracking.append(('and', other(self.tracking)))
    return other

  def __or__(self, other):
    log(f"__or__ {other}")
    self.tracking.append(('or', other(self.tracking)))
    return other

  def __gt__(self, other):
    log(f"__gt__ {other}")
    self.tracking[-1:][0].append(('>', other))
    return other

  def __lt__(self, other):
    log(f"__lt__ {other}")
    self.tracking[-1:][0].append(('<', other))
    return other

  def __add__(self, other):
    log(f"__add__ {other}")
    self.tracking.append(('add', other(self.tracking)))
    return other

  #def __rshift__(self, other):


def select(func):
  g = Ghost()
  r = func(g)
  return r.tracking