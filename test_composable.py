import composable

f = composable.Composable

f.enableLogging = True

inc = f(lambda x: x+1)
incPass = f(lambda x,y: (x+1, y+1))
power = f(lambda x,y: x**y)
splitNum = f(lambda x: (x/2, x/2))
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

def test_inverse_mixmatch():
  print("DEBUG FUNC:::::: test_inverse_mixmatch")
  func = incPass | power | withStr | strLen
  assert func(3, 3) == 3
  func2 = power | splitNum | incPass | f(lambda x,y: (x/2) + (x/2)) | withStr | strLen
  assert func2(4, 4) == 5
  
def rangeFactory(x):
  for i in range(1, x):
    yield i
  
def test_collections():
  print("DEBUG FUNC:::::: test_collections")
  pass2 = passthru | passthru | passthru
  assert pass2([1, 2, 3]) == [1, 2, 3]

def test_iterables():
  print("DEBUG FUNC:::::: test_iterables")
  rf = f(rangeFactory)
  evens = f(lambda r: filter(lambda x: x % 2 == 0, r))
  toList = f(lambda r: list(r))
  avg = f(lambda r: sum(r) / len(r))
  
  func = rf | evens | toList | avg
  
  assert func(10) == 5

def voidFunc():
  print(f"not input, not output")
  
def test_void():
  print("DEBUG FUNC:::::: test_void")
  vf = f(voidFunc)
  func = vf | vf | vf
  func()
  assert True, "does not throw"
  
def test_partialfunction():
  quad = f(lambda x: (x**2) + (8*x) + 12)
  domain = [1, 2, 3, 4, 5]
  fmap = f(lambda c: f(lambda d: map(c, d)))
  flist = f(list)
  
  comp = fmap(quad) | flist
  r = comp(domain)
  assert r == [21, 32, 45, 60, 77]
  
