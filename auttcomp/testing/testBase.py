import json
from types import SimpleNamespace
from .huggingFaceSample import sampleData_huggingFace
from .civitaiSample import civitaiStr

def jsonToObj(jsonStr):
  return json.loads(jsonStr, object_hook=lambda d: SimpleNamespace(**d))

def getHuggingFaceSample():
  return jsonToObj(sampleData_huggingFace)

def getCivitaiSample():
  return jsonToObj(civitaiStr)

