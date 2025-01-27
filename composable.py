from typing import Callable
from collections.abc import Iterable

class Composable:

  def __init__(self, func, nextFunc=None, parentComp=None):
    self.isChained = not parentComp is None
    self.parentComp = parentComp
    self.f: Callable[[()], ()] = func
    self.g: Callable[[()], ()] = nextFunc
    
  def __call__(self, *args, **extra):
    if self.isChained and self.g is None: return args
    fr = self.f( *args )
    if self.g is None: return fr #no composition
    garg = fr if isinstance(fr, Iterable) and not type(fr) is type("") else [a for a in [fr]]
    result = self.g( *fr )
    return result

  def __or__(self, other):
    if isinstance(other, Composable):
        return Composable(self, other.f, parentComp=self)
    else:
        raise TypeError(f"Unsupported operand type(s) for |: 'Composable' and '{type(other).__name__}'")

