import itertools, functools
from types import SimpleNamespace
from shapeEval import evalShape, distinctGenerator, deepYield


def test_distinct_generator():
  sut = distinctGenerator()
  sut.send([1, 2, 3, 3, 3, 1, 1, 4, 5])
  assert list(sut) == [1, 2, 3, 4, 5]


def test_deepYield_primitive_int():
  sut = deepYield()
  sut.value(123)
  assert sut.result() == 'int'


def test_deepYield_primitive_arr():
  sut = deepYield()
  input = [1, 2, 3]
  x = list(sut.iterList([1, 2, 3]))
  assert x == input
  assert sut.result() == ['int']


def xtest_deepYield_base_dict():
  #every document should be type {} or [] at root
  #todo exceptions for iter

  document = dict()
  document['foo'] = "bar"

  sut = deepYield()
  sut.add(document)
  sut.iterDict(vars(document).keys())

def xtest_deepYield_base_iter():
  #every document should be type {} or [] at root
  #todo exceptions for iter

  document = []
  document.append([1, 2, 3])

  sut = deepYield()
  sut.add(document)

def test_shapeEval_simple_objs():
  d = dict()
  d['foo'] = "bar"
  
  #assert evalShape(d) == {"foo": 'string'}
  
  l = [1, 2, 3]

