from ..quicklog import tracelog
from ..extensions import Api as f

@tracelog("test_partial_2_param_func")
def test_partial_2_param_func():
  quad = f(lambda x: (x ** 2) + (8 * x) + 12)
  domain = [1, 2, 3, 4, 5]
  fmap = f(map)
  flist = f(list)

  comp = fmap & quad | flist
  r = comp(domain)
  assert r == [21, 32, 45, 60, 77]


@tracelog("test_partial_3_param_func")
def test_partial_multi_param_func():
  mf = f(lambda xfilter, mapper, data: list(filter(xfilter, map(mapper, data))))
  square = f(lambda x: x ** 2)
  isEven = f(lambda x: x % 2 == 0)

  comp = mf & isEven & square

  assert comp([1, 2, 3, 4, 5]) == [4, 16]

@tracelog("test_partial_multi_param_funcs_value_binding")
def test_partial_multi_param_funcs_value_binding():
  mathx = f(lambda a, b, c, d: (a * b) / (c + d))
  comp = mathx & 2 & 5 & 1
  assert comp(1) == 5
  assert comp(9) == 1

@tracelog("test_partial_map")
def test_partial_map():
  cmap = f(map)
  square = lambda x: x ** 2
  comp = cmap & square
  assert list(comp([1, 2, 3])) == [1, 4, 9]
