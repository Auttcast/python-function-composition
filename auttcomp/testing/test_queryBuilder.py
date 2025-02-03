import traceback

from ..queryBuilder import *
from ..quicklog import *
'''


identity:   lambda x: x -> []
column:     lambda x: x[x.name] -> [[name]]
multi colum lambda x: x[x.name, x.foo] -> [[name, foo]]


'''
@tracelog("test_query_builder1", enable=True)
def test_query_builder1():

  def complexType():
    func2 = lambda x: (x.
                      models[x.left == "allen watts left", x.right == "allen watts right"] #where
                      .authorData[x.fullname1,x.fullname2, x.fullname3] #select
                      )
    r = func2(Ghost())
    print(list(r.tracking))
  complexType()
  # s = slice(0, 3, -2)
