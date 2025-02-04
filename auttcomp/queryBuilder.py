from collections.abc import Callable
from typing import Any, Union, Generic, TypeVar, Self, Iterable, Tuple

from .quicklog import log

printTracking = True

type EQ = '=='
type NEQ = '!='
type GT = '>'
type GE = '>='
type LT = '<'
type LE = '<='
type Conditional = Union[EQ | NEQ | GT | GE | LT | LE]


type ADD = 'add'
type AND = 'and'
type OR = 'or'



type GROUP = 'GROUP'

T = TypeVar('T')

class Ghost(Generic[T]):
  def __init__(self):
    super().__init__()
    self.tracking : T = list[T]()

  def __repr__(self):
    return "****SELF****"



  def __getattr__(self, name):
    if printTracking: log(f"__getattr__ {name}")
    self.tracking.append([name])
    if printTracking: log(self.tracking)
    return self

  def __getitem__(self, index):
    if printTracking: log(f"__getitem__ {index}")
    #if isinstance(index, Tuple) and len(index) > 1 and all(list(map(lambda x: isinstance(x, Ghost), index))):
    if isinstance(index, Tuple) and len(index) > 1:
      shift = -len(index)
      firstN = self.tracking[0:shift]
      mergedLastN = [i[0] for i in self.tracking[shift:]]
      self.tracking = firstN + [mergedLastN]

    #self.tracking.append(index.tracking)
    return self




  def __call__(self, *args, **kwargs):
    log(f"__call__ {args}")
    return self

  def __index__(self):
    log("index")

  def __bool__(self):
    log(f"__bool__")
    raise Exception("invalid expression: use == True|False instead")

  def __iter__(self):
    log('iter')

  def __contains__(self, item):
    log(f"__contains__ {item}")
    raise Exception("invalid operation - requires bool return")



  def __eq__(self, other):
    log(f"__eq__ {('==', other)}")
    self.tracking[-1:][0].append((EQ, other))
    return self

  def __ne__(self, other):
    log(f"__ne__ {('!=', other)}")
    self.tracking[-1:][0].append((NEQ, other))
    return self

  def __gt__(self, other):
    log(f"__gt__ {other}")
    self.tracking[-1:][0].append((GT, other))
    return self

  def __ge__(self, other):
    log(f"__ge__ {other}")
    self.tracking[-1:][0].append((GE, other))
    return self

  def __lt__(self, other):
    log(f"__lt__ {other}")
    self.tracking[-1:][0].append((LT, other))
    return self

  def __le__(self, other):
    log(f"__le__ {other}")
    self.tracking[-1:][0].append((LE, other))
    return self



  def __and__(self, other):
    log(f"__and__ {other}")
    self.tracking.append((AND, other(self.tracking)))
    return self

  def __or__(self, other):
    log(f"__or__ {other}")
    self.tracking.append((OR, other(self.tracking)))
    return self

  def __add__(self, other):
    log(f"__add__ {other}")
    self.tracking.append((AND, other(self.tracking)))
    return self


type Property = Union[str | [str, (Conditional, str)]]

def query(func:Callable[[Any], [[Property]]]) -> [[Property]]:
  g = Ghost[[Property]]()
  r = func(g)
  return r.tracking
