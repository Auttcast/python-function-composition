from composable import Composable
import shapeEval, functools

f = Composable

f.map = Composable(map)
f.filter = f(filter)
f.reduce = Composable(functools.reduce)
f.list = Composable(list)
f.distinct = Composable(lambda x: list(set(x))) #distinct does not work for complex types, should aggregate and compare
f.flatmap = Composable(lambda f, xs: [y for ys in xs for y in f(ys)])
f.shape = Composable(shapeEval.evalShape)
#any, all
#reverse