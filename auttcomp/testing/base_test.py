import json
from types import SimpleNamespace
from .hugging_face_sample import sample_data_hugging_face
from .civitai_sample import civitai_str

def json_to_obj(json_str):
  return json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))

def get_hugging_face_sample():
  return json_to_obj(sample_data_hugging_face)

def get_civitai_sample():
  return json_to_obj(civitai_str)
