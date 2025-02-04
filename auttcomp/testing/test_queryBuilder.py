from ..queryBuilder import *
from ..quicklog import *


'''
identity:   lambda x: x -> []
column:     lambda x: x[x.name] -> [[name]]
multi colum lambda x: x[x.name, x.foo] -> [[name, foo]]

func2 = lambda x: (x.
                      models[x.left == "allen watts left", x.right == "allen watts right"] #where
                      .authorData[x.fullname1,x.fullname2, x.fullname3] #select
                      )

models().




'''

isLogging = False

###SELECTION

@tracelog("test_query_builder_identity", enable=isLogging)
def test_query_builder_identity():
  r = select(lambda x: x)
  assert r == []

@tracelog("test_query_builder_property", enable=isLogging)
def test_query_builder_property():
  r = select(lambda x: x.model.FOO.bar)
  assert r == [['model'], ['FOO'], ['bar']]

@tracelog("test_query_builder_property_arr", enable=isLogging)
def xtest_query_builder_property_arr():
  r = select(lambda x: x.model[x.FOO.bar])
  print(r)
  assert r == [['model', [['FOO'], ['bar']]]]









# TODO

@tracelog("test_query_builder_property_condition", enable=isLogging)
def xtest_query_builder_property_condition():
  func = lambda x: x.model[x.prop == 1]
  r = func(Ghost()).tracking
  print(r)
  assert r == [['model'], ['prop', ('==', 1)]]

@tracelog("test_query_builder_property_condition2", enable=isLogging)
def xtest_query_builder_property_condition2():
  func = lambda x: x.model[x.prop1 == 1, x.prop2 == 2]
  r = func(Ghost()).tracking
  print(r)
  assert r == [['model'], ['prop1', ('==', 1)], ['prop2', ('==', 2)]]

@tracelog("test_query_builder_property_condition2_and", enable=isLogging)
def xtest_query_builder_property_condition2_and():
  func = lambda x: x.model[x.prop1 == True, x.prop2 != 2, x.prop2 != x.prop3]
  r = func(Ghost()).tracking
  print(r)
  assert r == [['model'], ['prop1', ('==', 1)]]




@tracelog("test_query_builder_property_condition_in", enable=isLogging)
def ztest_query_builder_property_condition_in():
  func = lambda x: x.model[x.prop in x[[1, 2]]]
  r = func(Ghost()).tracking
  print(r)
  assert r == [['model'], ['prop', ('==', 1)], ['prop', ('==', 2)]]
