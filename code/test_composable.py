import inspect

import composable, testBase
from quicklog import tracelog, log

f = composable.Composable

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
  inc5 = inc | inc | inc | inc
  assert inc5(1) == 5

@tracelog("test_single_multi_param")
def test_single_multi_param():
  (r0, r1) = incPass(1, 1)
  assert r0 == 2 and r1 == 2

@tracelog("test_multi_param")
def test_multi_param():
  incPass4 = incPass | incPass | incPass | incPass
  (r0, r1) = incPass4(1, 1)
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
  
def rangeFactory(x):
  for i in range(1, x):
    yield i
  
@tracelog("test_collections")
def test_collections():
  pass2 = passthru | passthru | passthru
  assert pass2([1, 2, 3]) == [1, 2, 3]

@tracelog("test_iterables")
def test_iterables():
  rf = f(rangeFactory)
  evens = f(lambda r: filter(lambda x: x % 2 == 0, r))
  toList = f(lambda r: list(r))
  avg = f(lambda r: sum(r) / len(r))
  
  func = rf | evens | toList | avg
  
  assert func(10) == 5

def voidFunc():
  log(f"not input, not output")

@tracelog("test_void")
def test_void():
  vf = f(voidFunc)
  func = vf | vf | vf
  func()
  assert True, "does not throw"

@tracelog("test_partial_2_param_func")
def test_partial_2_param_func():
  quad = f(lambda x: (x**2) + (8*x) + 12)
  domain = [1, 2, 3, 4, 5]
  fmap = f(map)
  flist = f(list)
  
  comp = fmap & quad | flist
  r = comp(domain)
  assert r == [21, 32, 45, 60, 77]
  
@tracelog("test_partial_2_nested_funcs")
def test_partial_1_param_nested_funcs():
  quad = f(lambda x: (x**2) + (8*x) + 12)
  domain = [1, 2, 3, 4, 5]
  fmap = f(lambda c: lambda d: map(c, d))
  flist = f(list)
  
  comp = fmap & quad | flist
  r = comp(domain)
  assert r == [21, 32, 45, 60, 77]
  
@tracelog("test_partial_3_param_func")
def test_partial_multi_param_func():

  mf = f(lambda xfilter, mapper, data: list(filter(xfilter, map(mapper, data))))
  square = f(lambda x: x**2)
  isEven = f(lambda x: x % 2 == 0)
  flist = f(list)
  
  comp = mf & isEven & square
  
  assert comp([1, 2, 3, 4, 5]) == [4, 16]
  
@tracelog("test_partial_multi_nested_funcs_value_binding")
def test_partial_multi_nested_funcs_value_binding():
  mathx = f(lambda a: lambda b: lambda c: lambda d: (a*b)/(c+d))
  comp = mathx & 2 & 5 & 1
  assert comp(1) == 5
  assert comp(9) == 1
  
@tracelog("test_partial_multi_param_funcs_value_binding")
def test_partial_multi_param_funcs_value_binding():

  mathx = f(lambda a, b, c, d: (a*b)/(c+d))
  comp = mathx & 2 & 5 & 1
  assert comp(1) == 5
  assert comp(9) == 1
  
@tracelog("test_dynamic_wrapping")
def test_dynamic_wrapping():

  #test_iterables without f-wrap
  rf = f(rangeFactory)
  evens = lambda r: filter(lambda x: x % 2 == 0, r)
  toList = lambda r: list(r)
  avg = lambda r: sum(r) / len(r)  
  func = rf | evens | toList | avg
  assert func(10) == 5

@tracelog("test_data_query")
def xtest_data_query():
  data = testBase.getSampleData()
  authorQuery = (f(lambda x: x.models) | f.map & (lambda x: x.author) | list ) (data)
  distinctAuthors = list(set(authorQuery))
  assert False
  
@tracelog("test_data_query2")
def xtest_data_query2():
  expectedAuthors = ['tencent', 'openbmb', 'deepseek-ai', 'microsoft', 'bytedance-research', 'unsloth', 'ostris', 'Qwen', 'HKUSTAudio', 'HuggingFaceTB', 'm-a-p', 'black-forest-labs', 'cyberagent', 'hexgrad', 'jinaai']
  
  data = testBase.getSampleData()
  actualAuthors = f(data.models) > f.map & (lambda x: x.author) | f.distinct
  assert expectedAuthors == actualAuthors
