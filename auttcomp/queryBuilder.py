from collections.abc import Callable
from typing import Iterable, Any, Union, Generic, TypeVar

from .quicklog import log

printTracking = True

type EQ = '=='
type NEQ = '!='
type AND = 'and'
type OR = 'or'
type GT = '>'
type LT = '<'
type ADD = 'add'

T = TypeVar('T')

class Ghost(Generic[T]):
  def __init__(self):
    super().__init__()
    self.tracking : T = []

  def __repr__(self):
    return "****SELF****"



  def __getattr__(self, name):
    if printTracking: log(f"__getattr__ {name}")
    self.tracking.append([name])
    if printTracking: log(self.tracking)
    return self

  def __getitem__(self, index):
    if printTracking: log(f"__getitem__ {index}")
    self.tracking.append(index.tracking)
    return None




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
    return other

  def __ne__(self, other):
    log(f"__ne__ {('!=', other)}")
    self.tracking[-1:][0].append((NEQ, other))
    return other

  def __and__(self, other):
    log(f"__and__ {other}")
    self.tracking.append((AND, other(self.tracking)))
    return other

  def __or__(self, other):
    log(f"__or__ {other}")
    self.tracking.append((OR, other(self.tracking)))
    return other

  def __gt__(self, other):
    log(f"__gt__ {other}")
    self.tracking[-1:][0].append((GT, other))
    return other

  def __lt__(self, other):
    log(f"__lt__ {other}")
    self.tracking[-1:][0].append((LT, other))
    return other

  def __add__(self, other):
    log(f"__add__ {other}")
    self.tracking.append((AND, other(self.tracking)))
    return other

type Operation = Union[EQ|NEQ|AND|OR|GT|LT|ADD]
type Const = Any
type Property = str
type SelectExpression = [Property]
type WhereExpression = [SelectExpression, [Property, (Operation, Union[Property|Any])]]

def select(func:Callable[[Any], [SelectExpression]]) -> [SelectExpression]:
  g = Ghost[SelectExpression]()
  r = func(g)
  return r.tracking

def where(func:Callable[[Any], WhereExpression]) -> WhereExpression:
  g = Ghost[WhereExpression]()
  r = func(g)
  return r.tracking
