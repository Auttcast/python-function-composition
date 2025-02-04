from ..expressionBuilder import *

from ..extensions import Api
from .testBase import getHuggingFaceSample
from ..quicklog import tracelog
f = Api

data = getHuggingFaceSample()

'''
identity:   lambda x: x -> []
column:     lambda x: x[x.name] -> [[name]]
multi colum lambda x: x[x.name, x.foo] -> [[name, foo]]
'''

isLogging = True

@tracelog("test_query_builder_identity")
def test_select_identity():
  r = f(data) > f.select(lambda x: x) | list
  assert r == f(data)

@tracelog("test_select_select")
def test_select_select():
  r = f(data) > f.select(lambda x: x.models.authorData.fullName) | list
  assert r == f(data.models) > f.map(lambda x: x.authorData) | f.map(lambda x: x.fullName) | list

@tracelog("test_select_where")
def test_select_where():
  r = f(data) > f.select(lambda x: x.models.authorData[x.fullName == "some name"]) | list
  assert r == [['models'], ['authorData'], ['fullName', (EQ, 'some name')]]

@tracelog("test_select_select_multi")
def test_select_select_multi():
  r = f(data) > f.select(lambda x: x.models.authorData[(x.fullName, x.isEnterprise)]) | list
  assert r == [['models'], ['authorData'], ['fullName', 'isEnterprise']]
