from ..queryBuilder import *
from ..quicklog import *

'''
identity:   lambda x: x -> []
column:     lambda x: x[x.name] -> [[name]]
multi colum lambda x: x[x.name, x.foo] -> [[name, foo]]
'''

isLogging = True

@tracelog("test_query_builder_identity")
def test_query_builder_identity():
  r = query(lambda x: x)
  assert r == []

@tracelog("test_query_builder_select")
def test_query_builder_select():
  r = query(lambda x: x.models.authorData.fullName)
  assert r == [['models'], ['authorData'], ['fullName']]

@tracelog("test_query_builder_where")
def test_query_builder_where():
  r = query(lambda x: x.models.authorData[x.fullName == "some name"])
  assert r == [['models'], ['authorData'], ['fullName', (EQ, 'some name')]]

@tracelog("test_query_builder_select_multi")
def test_query_builder_select_multi():
  r = query(lambda x: x.models.authorData[(x.fullName, x.isEnterprise)])
  assert r == [['models'], ['authorData'], ['fullName', 'isEnterprise']]
