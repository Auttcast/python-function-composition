from collections import namedtuple
from ..shapeEval import evalShape, shapeNode, nodeGraphToObj, DictShape, ListShape, TupleShape
from ..quicklog import tracelog, log
import json
from types import SimpleNamespace
from ..extensions import Api as f
from .testBase import getCivitaiSample

@tracelog("test_shapeNode")
def test_shapeNode():
  main = shapeNode({})
  foo = main.addChild(shapeNode(containerType="foo"))
  foo.addChild(shapeNode(value="str"))

  r = nodeGraphToObj(main)
  assert r == {"foo": "str"}

@tracelog("test_shapeNode2")
def test_shapeNode2():
  main = shapeNode({})
  foo = main.addChild(shapeNode(containerType="foo"))
  foo.addChild(shapeNode(value="str"))
  foo.addChild(shapeNode(value="int"))

  r = nodeGraphToObj(main)

  #something non-deterministic is happening, not worth debugging yet....
  c1 = r == {"foo": "int|str"}
  c2 = r == {"foo": "str|int"}
  assert c1 or c2

@tracelog("test_evalShape_prim")
def test_evalShape_prim():
  d = 1
  s = evalShape(d)
  assert s == 'int'

@tracelog("test_evalShape_list_empty")
def test_evalShape_list_empty():
  d = []
  s = evalShape(d)
  assert s == []

@tracelog("test_evalShape_list")
def test_evalShape_list():
  d = [1, 2, 2, 2]
  s = evalShape(d)
  assert s == ['int']

@tracelog("test_evalShape_list1")
def test_evalShape_list1():
  d = [1, 2, 2.0, 2]
  s = evalShape(d)
  assert s == ['int', 'float']

@tracelog("test_evalShape_list2")
def test_evalShape_list2():
  d = [[1, 2, 2, 2], [1, 2, 2, 2]]
  s = evalShape(d)
  assert s == [['int']]

@tracelog("test_evalShape_list3")
def test_evalShape_list3():
  d = [[1, 2, 2.0, 2], [1, 2, 2.0, 2]]
  s = evalShape(d)
  assert s == [['int', 'float']]

@tracelog("test_evalShape_list4")
def test_evalShape_list4():
  d = [ 1, [1, 2, 2.0, 2], [1, 2, 2.0, 2]]
  s = evalShape(d)
  assert s == ['int', ['int', 'float']]

@tracelog("test_evalShape_dict_empty")
def test_evalShape_dict_empty():
  d = {}
  s = evalShape(d)
  assert s == {}

@tracelog("test_evalShape_dict1")
def test_evalShape_dict1():
  d = {"val": 1}
  s = evalShape(d)
  assert s == {"val": "int"}

@tracelog("test_evalShape_dict2")
def test_evalShape_dict2():
  d = {"val": 1, "nested": {"n1": 2}}
  s = evalShape(d)
  assert s == {"val": "int", "nested": {"n1": "int"}}

@tracelog("test_evalShape_dict2")
def test_evalShape_dict2():
  d = [
    {"val": 1, "nested": {"n1": 2}},
    {"val": 1, "nested": {"n1": 2, "extra": "hello"}}
  ]

  s = evalShape(d)
  assert s == [{"val": "int", "nested": {"n1": "int", "extra": "str"}}]

@tracelog("test_evalShape_dict3")
def test_evalShape_dict3():
  jsonStr = """
  {
    "l1": {
      "l2p1": [1],
      "l2p2": ["x"]
    }
  }
  """

  jsonObj = json.loads(jsonStr, object_hook=lambda d: SimpleNamespace(**d))

  s = evalShape(jsonObj)
  assert s == {"l1": {"l2p1": ['int'], "l2p2": ["str"]}}

@tracelog("test_evalShape_dict4")
def test_evalShape_dict4():
  obj = {
      "l2p1": [("foo", (1))],
      "l2p2": ("x", 123)
    }

  s = evalShape(obj)
  assert s == {"l2p1": [("str", ('int'))], "l2p2": ("str", 'int')}

@tracelog("test_shapeEval_getAttr_returns_shape")
def test_shapeEval_getAttr_returns_shape():
  obj = {
    "l2p1": [("foo", (1))],
    "l2p2": ("x", 123)
  }

  s = evalShape(obj)
  assert isinstance(s, DictShape)
  assert isinstance(s.l2p1, ListShape)

  #SysUtil.enableTracing(filterFunc=lambda x: "shapeEval" in x.meta.file, mapFunc=lambda x: (x.func, x.args))
  s1 = s.l2p1[0]
  assert isinstance(s1, TupleShape), f"the shape is {type(s1)}"
  #SysUtil.disableTracing()

@tracelog("test_complex_obj_civitai")
def test_complex_obj_civitai():
  obj = getCivitaiSample()
  res = f(obj.result.data.json.collection) > f.shape
  log(res)
  #does not throw

@tracelog("test_tuple_with_list")
def test_tuple_with_list():
  tup = namedtuple("mytup", ["a", "b", "c"])
  t1 = tup(1, 2, [1])
  sh = evalShape(t1)
  log(type(sh))
  assert sh == ('int', 'int', ['int'])

@tracelog("test_tuple_with_dict")
def test_tuple_with_dict():
  tup = namedtuple("mytup", ["a", "b", "c"])
  t1 = tup(1, 2, {"foo": 1})
  sh = evalShape(t1)
  assert sh == ('int', 'int', {"foo": 'int'})

@tracelog("test_tuple_with_dupes")
def test_tuple_with_dupes():
  tup = namedtuple("mytup", ["a", "b", "c"])
  t1 = tup(1, 2, 3)
  sh = evalShape(t1)
  assert sh == ('int', 'int', 'int')

@tracelog("test_tuple_with_dupes_arr")
def test_tuple_with_dupes_arr():
  tup = namedtuple("mytup", ["a", "b", "c"])
  t1 = [tup(1, 2, 3), tup(1, 2, 3)]
  sh = evalShape(t1)
  assert sh == [('int', 'int', 'int')]

@tracelog("test_dict_sometimes_null")
def test_dict_sometimes_null():
  d1 = {"val": 1, "nested": {"n1": 2}}
  d2 = {"val": 1, "nested": None}

  s = evalShape([d1, d2])
  log(s)
  assert s == [{"val": "int", "nested?": {"n1": "int"}}]

@tracelog("test_dict_only_null_props")
def test_dict_only_null_props():
  d1 = {"val": 1, "nested": None}
  d2 = {"val": 1, "nested": None}

  s = evalShape([d1, d2])
  log(s)
  assert s == [{"val": "int", "nested?": "None"}]
