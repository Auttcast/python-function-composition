from types import SimpleNamespace
from quicklog import tracelog
import quicklog
from extensions import Api as f

def getDicts():
  normalDict = {"a": {"b": 123, "c":{"d": "eeee"}}}
  simp = SimpleNamespace(**normalDict.copy())
  return [normalDict, normalDict['a'], simp.a]

def getIterables():
  return [set(), [1, 2]]

def getCommonAttrs(objArray):
  if len(objArray) == 1: return objArray
  reduced = (f(objArray)
             > f.map(dir)
             | f.reduce(lambda x, y: set(x).intersection(set(y))) | list)

  return reduced

@tracelog("test_eval_distinct_attrs")
def test_eval_distinct_attrs():
  dicts = getDicts()
  iters = getIterables()

  dictCommonAttrs = set(getCommonAttrs(dicts))
  itersCommonAttrs = set(getCommonAttrs(iters))

  quicklog.log(f"dictCommonAttrs::::: {dictCommonAttrs}\n\n")
  quicklog.log(f"itersCommonAttrs::::: {itersCommonAttrs}\n\n")

  listId = itersCommonAttrs.difference(dictCommonAttrs)
  dictId = dictCommonAttrs.difference(itersCommonAttrs)

  quicklog.log(f"listId::::: {listId}\n\n")
  quicklog.log(f"dictId::::: {dictId}\n\n")
