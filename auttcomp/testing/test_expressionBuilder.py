from ..extensions import Api
from .testBase import getHuggingFaceSample
from ..quicklog import tracelog
from ..utility import SysUtil
f = Api

data = getHuggingFaceSample()

isLogging = True

@tracelog("test_query_builder_identity")
def test_select_identity():
  r = f(data) > f.select(lambda x: x) | list
  assert r == [f(data)()]

@tracelog("test_select_select")
def test_select_select():
  r = f(data) > f.select(lambda x: x.models.authorData.fullname) | list
  assert r == (f(data.models) > f.map(lambda x: x.authorData) | f.map(lambda x: x.fullname) | list)
