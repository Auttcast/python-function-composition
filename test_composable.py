import math, composable

f = composable.Composable

inc = f(lambda x: x+1)
incPass = f(lambda x,y: (x+1, y+1))
power = f(lambda x,y: x**y)
withStr = f(lambda x: (x, str(x)))
strLen = f(lambda x,y: len(y))
passthru = f(lambda x: x)

def foo():
  return None

  def test_debug():
    
    inc1 = f(lambda x: x+1)
    inc2 = f(lambda x: x+2)
    inc3 = f(lambda x: x+3)
    inc4 = f(lambda x: x+4)
    inc5 = f(lambda x: x+5)
    
    inc1.name = "inc1"
    inc2.name = "inc2"
    inc3.name = "inc3"
    inc4.name = "inc4"
    inc5.name = "inc5"
    
    func = inc1 | inc2 | inc3 | inc4 | inc5
    assert func(1) == 16

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
    
  def te_iterables2():
    rf = f(rangeFactory)
    evens = f(lambda r: filter(lambda x: math.fmod(x, 2)[1] == 0, r))
    toList = f(list)
    avg = f(lambda r: sum(r) / len(r))
    
    func = rf | evens | toList | avg
    
    assert func(10) == 5
    
