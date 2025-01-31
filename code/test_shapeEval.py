import shapeEval, json
from shapeEval import evalShape, shapeNode
from types import SimpleNamespace
from quicklog import tracelog

@tracelog("test_shapeNode")
def test_shapeNode():
  main = shapeNode({})
  foo = main.addChild(shapeNode(containerType="foo"))
  foo.addChild(shapeNode(value="str"))

  r = shapeEval.nodeGraphToObj(main)
  assert r == {"foo": "str"}

@tracelog("test_shapeNode2")
def test_shapeNode2():
  main = shapeNode({})
  foo = main.addChild(shapeNode(containerType="foo"))
  foo.addChild(shapeNode(value="str"))
  foo.addChild(shapeNode(value="int"))

  r = shapeEval.nodeGraphToObj(main)
  assert r == {"foo": "str|int"}

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
