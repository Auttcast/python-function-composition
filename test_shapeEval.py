import composable, itertools, functools, json
from types import SimpleNamespace

def createTestData():
  doc = json.loads(open('sample.json').read(), object_hook=lambda d: SimpleNamespace(**d))
  return doc
  
def xtestSnippet():
  import composable, itertools, functools, json, pprint
  from types import SimpleNamespace
  data = json.loads(open('sample.json').read(), object_hook=lambda d: SimpleNamespace(**d))
  result = f(data) > f.shape
  pprint.pprint(result, indent=2)

