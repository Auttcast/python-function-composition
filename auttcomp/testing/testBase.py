import json
from types import SimpleNamespace
from .sample import sampleData_huggingFace

def getHuggingFaceSample():
  doc = json.loads(sampleData_huggingFace, object_hook=lambda d: SimpleNamespace(**d))
  return doc

