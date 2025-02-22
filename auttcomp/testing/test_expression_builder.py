from ..extensions import Api as f
from .base_test import get_hugging_face_sample
from ..quicklog import tracelog

data = get_hugging_face_sample()

#NOTE - experimental work in progress

@tracelog("test_select_identity")
def test_select_identity():
  r = f.id(data) > f.select(lambda x: x) | list
  assert r == [f.id(data)()]

@tracelog("test_select")
def test_select():
  r = f.id(data) > f.select(lambda x: x.models.authorData.fullname) | list
  assert r == (f.id(data.models) > f.map(lambda x: x.authorData) | f.map(lambda x: x.fullname) | list)

@tracelog("test_property_as_expression")
def test_property_as_expression():
  assert (f.id(data) > f.select(lambda x: x.models)) == (f.id(data) > f.at(lambda x: x.models))
  assert (f.id(data) > f.select(lambda x: x.models.authorData)) == (f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.authorData) | list)
