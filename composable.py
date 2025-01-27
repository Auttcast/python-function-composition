from typing import Callable
from collections.abc import Iterable

#todo
#github?
#unit test cases:
#various output/input types and param args
#using the same function in multiple chains
#exception handling
#chains which range in number of parameters
#can it support memoization?

#Description
#This is a simple class that overrides the | operator allowing for cleaner composition
#How does it work?
#incFunc = f(lambda x: x+1)
#addThree = incFunc | incFunc | incFunc
#r = addThree(5)
#the result is 5.
#The Comp class applies what is necessary to compose function calls together with pipe |
#The Comp class itself is also considered an executable lambda
#When a composition is created with f | g, a new Comp object is return which simply contains pointers to either function
#If additional functions are chained, the pointers are updated.

class Comp:

  def __init__(self, func, nextFunc=None, parentComp=None):
    self.isChained = not parentComp is None
    self.parentComp = parentComp
    self.f: Callable[[()], ()] = func
    self.g: Callable[[()], ()] = nextFunc
    
  def __call__(self, *args, **extra):
    if self.isChained and self.g is None: return args
    c1 = self.f( *args )
    if self.g is None: return c1 #no composition
    garg = c1 if isinstance(c1, Iterable) and not type(c1) is type("") else [a for a in [c1]]
    result = self.g( *garg )
    return result

  def __or__(self, other):
    if isinstance(other, Comp):
        return Comp(self, other.f, parentComp=self)
    else:
        raise TypeError(f"Unsupported operand type(s) for |: 'Comp' and '{type(other).__name__)}'")

