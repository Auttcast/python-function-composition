from ..extensions import Api
from .testBase import getSampleData
from ..quicklog import tracelog

f = Api

data = getSampleData()

@tracelog("test_at")
def test_at():
  sr = f(data) > f.shapeObj | f.at(lambda x: x.models) 
  assert "author" in sr[0].keys()

@tracelog("test_map")
def test_map():
  r1 = f(data) > f.shapeObj | f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
  assert r1 == ['str']

@tracelog("test_author_query")
def test_author_query():
  schemaQuery = f(data) > f.shapeObj | f.at(lambda x: x.models) | f.map(lambda x: x.author) | list
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
  dataQuery = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | f.take(3) | list
  assert len(dataQuery) == 3

@tracelog("test_skip")
def test_skip():
  dataQuery = f(data) > f.at(lambda x: x.models) | f.map(lambda x: x.author) | f.distinct | f.skip(3) | list
  assert len(dataQuery) == 12

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
  valueSelect = lambda x: x[0][1]
  j = f(resCountByAuthor) > f.innerJoin(likesByAuthor, keySelect, keySelect, valueSelect, valueSelect) | list

  assert j == [('deepseek-ai', (14027, 12)), ('bytedance-research', (221, 2)), ('Qwen', (596, 4))]

@tracelog("test_hackery", enable=True)
def test_hackery():

  class Foo():
    def __init__(self, tracking=[]):
      self.tracking = tracking

    def __getattr__(self, name):
      return Foo(self.tracking + [name])

    def __getitem__(self, index):

      #select format (index is param tracker)
      print(f"index: {index[0].tracking[0], index[1].tracking[0], index[2].tracking[0]}")

      #where format (index is selector func
      #self.tracking.append(index(Foo()).tracking)
      return self

    def __gt__(self, other):
      self.tracking.append(('>', other))
      return self

    def __lt__(self, other):
      self.tracking.append(('<', other))
      return self

    def __eq__(self, other):
      self.tracking.append(('==', other))
      return self

    def __and__(self, other):
      self.tracking.append(('and', other(self.tracking)))
      #join?
      return self

    def __bool__(self):
      raise Exception("invalid operation - not allowed to return anything other than bool")

    def __call__(self, *args, **kwargs):
      return self.tracking

    def __or__(self, other):
      self.tracking.append(('or', other))
      #composition or filtering
      return self

    def __contains__(self, item):
      raise Exception("invalid operation - requires bool return")

    def __add__(self, other):
      self.tracking.append(('add', other(self.tracking)))
      return self



  #tabular data

  def tabulartype():
    xParam = Foo()

    func = lambda x: x[x.id, x.name, x.age]

    r = func(xParam)
    print(r.tracking)

  tabulartype()






  def complexType():
    xParam = Foo()

    func = lambda x: (x.
                      models[lambda x2: x2.author == "allen watts"] #where
                      .authorData[x.fullname, x.type, x.followerCount] #select
                      )

    r = func(xParam)
    print(r.tracking)

  # s = slice(0, 3, -2)

  #using index accessor to filter
  #func = lambda x: x.models[where(lambda x: x.author == "allen watts")].authorData.followerCount
  #note slice is sealed

  #func = lambda x: x.models[where(lambda x: x.author == "allen watts")].authorData[select([id, avatar, name])]


  # {} [] {} prop
  # get map get get
  # flatmap for each [] in path
  # where x.models.authorData.downloads > 10000
  #graph monad / chain
  # graph(query) -> monad; filter, etc; -> project
  # conditional api:
  # - must separate path from evaluation
  # - .graphWhere(lambda x.models.authorData.downloads, lambda x: x >
  #

  #
  # r = func(Foo())
  # print(r.tracking)
  #print(r.tracking[5][1])
