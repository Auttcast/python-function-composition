import json
from types import SimpleNamespace
from .sample import sampleData

def getSampleData():
  doc = json.loads(sampleData, object_hook=lambda d: SimpleNamespace(**d))
  return doc

