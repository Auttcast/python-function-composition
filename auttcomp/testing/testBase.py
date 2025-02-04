import json
from types import SimpleNamespace
from .sample import sampleData_huggingFace

def getSampleData():
  doc = json.loads(sampleData_huggingFace, object_hook=lambda d: SimpleNamespace(**d))
  return doc

