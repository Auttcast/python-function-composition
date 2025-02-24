from typing import Callable
from ..quicklog import tracelog, log
from ..composable import Composable
from ..extensions import Api as f

@tracelog("test_partial_1_param_func")
def test_partial_1_param_func():
  cat1 = f(lambda x: "0" + x)
  get = cat1 & "1"
  assert isinstance(get, Composable)
  assert get() == "01"

@tracelog("test_partial_2_param_func")
def test_partial_2_param_func():
  cat2_l:Callable[[str, str], str] = lambda a, b: "0" + a + b
  cat2 = f(cat2_l)
  get1 = cat2 & "1"
  assert get1("2") == "012"

  get2 = get1 & "2"
  assert get2() == "012"

  get = cat2 & "1" & "2"
  assert get() == "012"

@tracelog("test_partial_3_param_func")
def test_partial_multi_param_func():
  cat3 = f(lambda a, b, c: "0" + a + b + c)
  get1 = cat3 & "1"
  assert get1("2", "3") == "0123"

  get2 = cat3 & "1" & "2"
  assert get2("3") == "0123"

  get3 = cat3 & "1" & "2" & "3"
  assert get3() == "0123"

@tracelog("test_partial_3_param_func_curried")
def test_partial_multi_param_func():

  #this test demonstrates that when functions are already curried, they are not within the composable's domain

  cat3 = f(lambda a: lambda b: lambda c: "0" + a + b + c)
  get1 = cat3("1")
  assert get1("2")("3") == "0123"

  #NOT composable!
  assert not isinstance(get1, Composable)

  get2 = cat3("1")("2")
  assert get2("3") == "0123"

  get3 = cat3("1")("2")("3")
  assert get3 == "0123"

@tracelog("test_partial_on_no_param_throws")
def test_partial_on_no_param_throws():
  zero_param_func = f(lambda: "hi")

  try:
    zero_param_func & "1"
    assert False, "expected to throw!"
  except TypeError:
    pass
  except Exception:
    assert False, "wrong exception type"

@tracelog("test_partial_on_curried_composable_func")
def test_partial_on_curried_composable_func():
  
  curried_add = f(lambda x: f(lambda y: x + y))

  curried_add_1 = curried_add & 1

  assert curried_add_1(1) == 2
  
@tracelog("test_partial_callable_class")
def test_partial_callable_class():
  
  data = [1, 2, 3]
  plus1 = f(map) & (lambda x: x + 1)
  expected = [2, 3, 4]

  actual = list(plus1(data))

  assert actual == expected
