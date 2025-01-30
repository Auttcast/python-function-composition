import itertools, functools
from types import SimpleNamespace
from shapeEval import evalShape


def test_shapeEval_simple_objs():
  d = dict()
  d['foo'] = "bar"
  
  assert evalShape(d) == {"foo": 'bar'}
  
  l = [1, 2, 3]

