from ..extensions import Api
from .testBase import getHuggingFaceSample
from ..quicklog import tracelog, log

f = Api

data = getHuggingFaceSample()

@tracelog("test_at")
def test_at():
  sr = f(data) > f.shape | f.at(lambda x: x.models)
  log('test123')
  assert "author" in sr[0].keys()

@tracelog("test_map")
def test_map():
  log('test456')
  r1 = f(data) > f.shape | f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
  assert r1 == ['str']

@tracelog("test_author_query")
def test_author_query():
  schemaQuery = f(data) > f.shape | f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
  dataQuery = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | list

  assert schemaQuery == ['str']
  assert dataQuery[0] == 'deepseek-ai'

@tracelog("test_filter")
def test_filter():
  dataQuery = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | f.filter(lambda x: "deep" in x)| list
  assert dataQuery == ["deepseek-ai"]

@tracelog("test_reduce")
def test_reduce():
  s1 = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.downloads) | list
  dataQuery = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.downloads) | f.reduce2(lambda x, y: x+y, 0)
  assert dataQuery == sum(s1)

@tracelog("test_flatmap")
def test_flatmap():
  dataQuery = f(data) > f.at(lambda x: x.models) | f.flatmap(lambda x: x.widgetOutputUrls) | list
  assert dataQuery == ['foo', 'foo1', 'foo2', 'foo2']

@tracelog("test_reverse")
def test_reverse():
  dataQuery = f(data) > f.at(lambda x: x.models) | f.flatmap(lambda x: x.widgetOutputUrls) | list | f.reverse | list
  assert dataQuery == ['foo2', 'foo2', 'foo1', 'foo']

@tracelog("test_any")
def test_any():
  dataQuery = f(data) > f.at(lambda x: x.models) | f.flatmap(lambda x: x.widgetOutputUrls) | f.any(lambda x: "1" in x)
  assert dataQuery

@tracelog("test_all")
def test_all():
  dataQuery = f(data) > f.at(lambda x: x.models) | f.flatmap(lambda x: x.widgetOutputUrls) | f.all(lambda x: "oo" in x)
  assert dataQuery

@tracelog("test_sort")
def test_sort():
  dataQuery = f(['z', 'x', 'a', 'b']) > f.sort | list
  assert dataQuery == ['a', 'b', 'x', 'z']

@tracelog("test_take")
def test_take():
  dist = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | list
  dataQuery = f(dist) > f.take(3) | list
  assert dataQuery == (f(dist) > f.list)[0:3]

@tracelog("test_skip")
def test_skip():
  dist = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | list
  dataQuery = f(dist) > f.skip(3) | list
  assert len(dataQuery) == len(dist[3:])
  assert dataQuery == dist[3:]

@tracelog("test_sortBy")
def test_sortBy():
  unsortedAuthors = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
  nativeSortedAuthors = sorted(unsortedAuthors)
  fsortedAuthors = f(data) > f.at(lambda x: x.models) | f.sortBy(lambda x: x.author) | f.map(lambda x: x.author) | list

  assert fsortedAuthors == nativeSortedAuthors

@tracelog("test_group")
def test_group():
  groupByAuthor = (f(data) > f.at(lambda x: x.models)
                   | f.group(lambda x: x.author)
                   | f.map(lambda g: (g.key, len(g.value)))
                   | f.sortByDescending(lambda x: x[1])
                   | f.take(1)
                   | list)
  assert groupByAuthor == [('deepseek-ai', 12)]


@tracelog("test_join")
def test_join():

  groupByAuthor = f(data) > f.at(lambda x: x.models) | f.group(lambda x: x.author) | f.tee

  resCountByAuthor = (
      f(groupByAuthor)
      > f.tee
      | f.map(lambda g: (g.key, len(g.value)))
      | f.sortByDescending(lambda x: x[1])
      | f.take(3)
      | list
  )

  def selectManyLikes(arr):
    return f(arr) > f.flatmap(lambda x: x.likes) | sum

  likesByAuthor = (
    f(groupByAuthor)
    > f.tee
    | f.map(lambda g: (g.key, selectManyLikes(g.value)))
    | list
  )

  keySelect = lambda x: x[0]
  j = f(resCountByAuthor) > f.innerJoin(likesByAuthor, keySelect, keySelect, lambda l, r: (l[0][1], r[0][1])) | list

  assert j == [('deepseek-ai', (14027, 12)), ('bytedance-research', (221, 2)), ('Qwen', (596, 4))]

@tracelog("test_distinctSet")
def test_distinctSet():
  data = f([1, 2, 3, 3, 3, 3])
  slowDistinct = data > f.distinct
  fastDistinct = data > f.distinctSet
  assert slowDistinct == fastDistinct


@tracelog("test_property_as_expression")
def test_property_as_expression():

  assert (f(data) > f.select(lambda x: x.models)) == (f(data) > f.at(lambda x: x.models))
  assert (f(data) > f.select(lambda x: x.models.authorData)) == (f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.authorData) | list)
