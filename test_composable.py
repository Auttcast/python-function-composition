import math, composable

f = composable.Composable

inc = f(lambda x: x+1)
incPass = f(lambda x,y: (x+1, y+1))
power = f(lambda x,y: x**y)
withStr = f(lambda x: (x, str(x)))
strLen = f(lambda x,y: len(y))
passthru = f(lambda x: x)

def test_minimal_single_param():
  print("DEBUG FUNC:::::: test_minimal_single_param")
  assert inc(1) == 2

def test_basic_comp():
  print("DEBUG FUNC:::::: test_basic_comp")
  inc2 = inc | inc
  assert inc2(1) == 3

def test_long_comp():
  print("DEBUG FUNC:::::: test_long_comp")
  inc5 = inc | inc | inc | inc
  assert inc5(1) == 5

def test_single_multi_param():
  print("DEBUG FUNC:::::: test_single_multi_param")
  (r0, r1) = incPass(1, 1)
  assert r0 == 2 and r1 == 2
  
def test_multi_param():
  print("DEBUG FUNC:::::: test_multi_param")
  incPass4 = incPass | incPass | incPass | incPass
  (r0, r1) = incPass4(1, 1)
  assert r0 == 5 and r1 == 5

def test_various_param():
  print("DEBUG FUNC:::::: test_various_param")
  func = incPass | power | withStr | strLen
  assert func(3, 3) == 3

def rangeFactory(x):
  for i in range(1, x):
    yield i
  
def test_collections():
  pass2 = passthru | passthru | passthru
  assert pass2([1, 2, 3]) == [1, 2, 3]

def test_iterables():
  rf = f(rangeFactory)
  evens = f(lambda r: filter(lambda x: x % 2 == 0, r))
  toList = f(lambda r: list(r))
  avg = f(lambda r: sum(r) / len(r))
  
  func = rf | evens | toList | avg
  
  assert func(10) == 5

def voidFunc(x):
  print(f"I don't return anything! {x}")
  
def voidFunc2():
  print(f"not input, not output")
  
def test_void():
  vf = f(voidFunc2)
  func = vf | vf | vf
  func()
  assert True, "does not throw"
