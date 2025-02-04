from types import SimpleNamespace

from ..quicklog import tracelog, log
from ..utility import SysUtil
import sys
from ..queryBuilder import select

@tracelog("test_SysUtil")
def test_SysUtil():

  def baz(x):
    return sys._getframe()

  def bar(a, b):
    addFac = 1
    return baz(a+addFac+b+addFac)

  def foo(a, b, c):
    addFac = 1
    a = a+addFac
    b = b+addFac
    c = c+addFac
    return bar(a+b, c)

  cf = foo(5, 5, 5)

  assert SysUtil.getCallArgs(cf, withData=True) == SimpleNamespace(**{"x": 20})
  assert SysUtil.getCallArgs(cf.f_back, withData=True) == SimpleNamespace(**{"a": 12, "b": 6})

  #locals are provided by the frame, mutated thru execution
  assert SysUtil.getCallArgs(cf.f_back.f_back, withData=True) == SimpleNamespace(**{"a": 6, "b": 6, "c": 6})

  assert cf.f_code.co_name == "baz"
  assert cf.f_back.f_code.co_name == "bar"
  assert cf.f_back.f_back.f_code.co_name == "foo"

  #assert cf.f_back.f_back.f_code.f_locals == ('x')


