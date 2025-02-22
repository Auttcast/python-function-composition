from ..extensions import Api as f
from .base_test import get_hugging_face_sample
from ..quicklog import tracelog, log

data = get_hugging_face_sample()


@tracelog("test_at")
def test_at():
  sr = f.id(data) > f.shape | f.at(lambda x: x.models)
  assert "author" in sr[0].keys()

@tracelog("test_map")
def test_map():
  r1 = f.id(data) > f.shape | f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
  assert r1 == ['str']

@tracelog("test_author_query")
def test_author_query():
  schema_query = f.id(data) > f.shape | f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
  data_query = f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | list

  assert schema_query == ['str']
  assert data_query[0] == 'deepseek-ai'

@tracelog("test_filter")
def test_filter():
  data_query = f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | f.filter(lambda x: "deep" in x) | list
  assert data_query == ["deepseek-ai"]

@tracelog("test_reduce")
def test_reduce():
  s1 = f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.downloads) | list
  data_query = f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.downloads) | f.reduce2(lambda x, y: x+y, 0)
  assert data_query == sum(s1)

@tracelog("test_flatmap")
def test_flatmap():
  data_query = (f.id(data) > f.at(lambda x: x.models)
               | f.filter(lambda x: hasattr(x, 'widgetOutputUrls') and x.widgetOutputUrls is not None)
               | f.flatmap(lambda x: x.widgetOutputUrls)
               | list)
  assert data_query == ['foo', 'foo1', 'foo2', 'foo2']

@tracelog("test_flatmapid")
def test_flatmapid():
  arr = [[1]]*3
  res = f.id(arr) > f.flatmapid | list
  assert res == [1, 1, 1]

@tracelog("test_reverse")
def test_reverse():
  data_query = (f.id(data) > f.at(lambda x: x.models)
               | f.filter(lambda x: hasattr(x, 'widgetOutputUrls') and x.widgetOutputUrls is not None)
               | f.flatmap(lambda x: x.widgetOutputUrls)
               | f.reverse
               | list)
  assert data_query == ['foo2', 'foo2', 'foo1', 'foo']

@tracelog("test_any")
def test_any():
  data_query = (f.id(data) > f.at(lambda x: x.models)
               | f.filter(lambda x: hasattr(x, 'widgetOutputUrls') and x.widgetOutputUrls is not None)
               | f.flatmap(lambda x: x.widgetOutputUrls)
               | f.any(lambda x: "1" in x))
  assert data_query

@tracelog("test_all")
def test_all():
  data_query = (f.id(data) > f.at(lambda x: x.models)
               | f.filter(lambda x: hasattr(x, 'widgetOutputUrls') and x.widgetOutputUrls is not None)
               | f.flatmap(lambda x: x.widgetOutputUrls)
               | f.all(lambda x: "oo" in x))
  assert data_query

@tracelog("test_sort")
def test_sort():
  data_query = f.id(['z', 'x', 'a', 'b']) > f.sort | list
  assert data_query == ['a', 'b', 'x', 'z']

@tracelog("test_take")
def test_take():
  dist = f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | list
  data_query = f.id(dist) > f.take(3) | f.list
  assert data_query == (f.id(dist) > f.list)[0:3]

@tracelog("test_skip")
def test_skip():
  dist = f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | list
  data_query = f.id(dist) > f.skip(3) | f.list
  assert len(data_query) == len(dist[3:])
  assert data_query == dist[3:]

@tracelog("test_sort_by")
def test_sort_by():
  unsorted_authors = f.id(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
  native_sorted_authors = sorted(unsorted_authors)
  fsorted_authors = f.id(data) > f.at(lambda x: x.models) | f.sort_by(lambda x: x.author) | f.map(lambda x: x.author) | list

  assert fsorted_authors == native_sorted_authors

@tracelog("test_group")
def test_group():
  group_by_author = (f.id(data) 
                    > f.at(lambda x: x.models)
                    | f.group(lambda x: x.author)
                    | f.map(lambda g: (g.key, len(g.value)))
                    | f.sort_by_descending(lambda x: x[1])
                    | f.take(1)
                    | list)

  assert group_by_author == [('deepseek-ai', 12)]


@tracelog("test_join")
def test_join():

  group_by_author = f.id(data) > f.at(lambda x: x.models) | f.group(lambda x: x.author) | f.tee

  res_count_by_author = (
      f.id(group_by_author)
      > f.tee
      | f.map(lambda g: (g.key, len(g.value)))
      | f.sort_by_descending(lambda x: x[1])
      | f.take(3)
      | list
  )

  def sum_many_likes(arr):
    return f.id(arr) > f.map(lambda x: x.likes) | sum

  likes_by_author = (
    f.id(group_by_author)
    > f.tee
    | f.map(lambda g: (g.key, sum_many_likes(g.value)))
    | list
  )

  key_select = lambda x: x[0]
  
  join = (f.id(res_count_by_author) > f.inner_join(
      likes_by_author,
      key_select,
      key_select,
      lambda l: l[0][1],
      lambda r: r[0][1]
  ) | list)

  assert join == [('deepseek-ai', (14027, 12)), ('bytedance-research', (221, 2)), ('Qwen', (596, 4))]

@tracelog("test_distinct_set")
def test_distinct_set():
  arr = f.id([1, 2, 3, 3, 3, 3])
  slow_distinct = arr > f.distinct
  fast_distinct = arr > f.distinct_set
  assert slow_distinct == fast_distinct

