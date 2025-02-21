from ..quicklog import tracelog, log
from ..extensions import Api as f

inc = f(lambda x: x+1)
incPass = f(lambda x,y: (x+1, y+1))
power = f(lambda x,y: x**y)
splitNum = f(lambda x: (x/2, x/2))
withStr = f(lambda x: (x, str(x)))
strLen = f(lambda x,y: len(y))
passthru = f(lambda x: x)

@tracelog("test_minimal_single_param")
def test_minimal_single_param():
  assert inc(1) == 2

@tracelog("test_basic_comp")
def test_basic_comp():
  inc2 = inc | inc
  assert inc2(1) == 3

@tracelog("test_long_comp")
def test_long_comp():
  inc4 = inc | inc | inc | inc
  assert inc4(1) == 5

@tracelog("test_single_multi_param")
def test_single_multi_param():
  (r0, r1) = incPass(1, 1)
  assert r0 == 2 and r1 == 2

@tracelog("test_multi_param")
def test_multi_param():
  inc_pass4 = incPass | incPass | incPass | incPass
  (r0, r1) = inc_pass4(1, 1)
  assert r0 == 5 and r1 == 5

@tracelog("test_various_param")
def test_various_param():
  func = incPass | power | withStr | strLen
  assert func(3, 3) == 3

@tracelog("test_inverse_mixmatch")
def test_inverse_mixmatch():
  func = incPass | power | withStr | strLen
  assert func(3, 3) == 3
  func2 = power | splitNum | incPass | f(lambda x,y: (x/2) + (x/2)) | withStr | strLen
  assert func2(4, 4) == 5

@tracelog("test_collections")
def test_collections():
  pass3 = passthru | passthru | passthru
  assert pass3([1, 2, 3]) == [1, 2, 3]

def range_factory(x):
  for i in range(1, x):
    yield i

@tracelog("test_iterables")
def test_iterables():
  rf = f(range_factory)
  evens = f(lambda r: filter(lambda x: x % 2 == 0, r))
  to_list = f(lambda r: list(r))
  avg = f(lambda r: sum(r) / len(r))
  
  func = rf | evens | to_list | avg
  
  assert func(10) == 5

def void_func():
  log(f"not input, not output")

@tracelog("test_void")
def test_void():
  vf = f(void_func)
  func = vf | vf | vf
  func()
  assert True, "does not throw"

@tracelog("test_dynamic_wrapping")
def test_dynamic_wrapping():

  #test_iterables without f-wrap
  rf = f(range_factory)
  evens = lambda r: filter(lambda x: x % 2 == 0, r)
  to_list = lambda r: list(r)
  avg = lambda r: sum(r) / len(r)  
  func = rf | evens | to_list | avg
  assert func(10) == 5
