from ..queryBuilder import *
from ..quicklog import *
'''


identity:   lambda x: x -> []
column:     lambda x: x[x.name] -> [[name]]
multi colum lambda x: x[x.name, x.foo] -> [[name, foo]]


'''
@tracelog("test_query_builder1", enable=True)
def test_query_builder1():

  #tabular data
  #[['id', 'name', 'age']]
  def tabulartype():
    tabParam = Ghost()
    func1 = lambda x: x[x.id, x.name, x.age]

    tr = func1(tabParam)
    print(tr.tracking)

  #lambda: ['models', ['author', ('==', 'allen watts')], 'authorData', ['fullname', 'type', 'followerCount']]
  #tuple:  ['models', ['author', ('==', 'allen watts')], 'authorData', ['fullname', 'type', 'followerCount']]

  #  access         filter                            access               select
  #['models', ['author', ('==', 'allen watts')], 'authorData', ['fullname', 'type', 'followerCount']]
  def complexType():
    complexParam = Ghost()
    #['author', ('==', 'allen watts')]
    func2 = lambda x: (x.
                      models[x.left == "allen watts left"] #where
                      .authorData[x.fullname, x.fullname] #select
                      )
    r = func2(complexParam)
    print(r.tracking)
  complexType()
  # s = slice(0, 3, -2)

  #using index accessor to filter
  #func = lambda x: x.models[where(lambda x: x.author == "allen watts")].authorData.followerCount
  #note slice is sealed

  #func = lambda x: x.models[where(lambda x: x.author == "allen watts")].authorData


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
