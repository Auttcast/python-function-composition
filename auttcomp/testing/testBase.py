import json
from types import SimpleNamespace

def getSampleData():
  doc = json.loads(open('sample.json').read(), object_hook=lambda d: SimpleNamespace(**d))
  return doc

