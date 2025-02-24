from typing import Union, Self, Any
import sys
import pprint
import io

class ShapeNode:
  def __init__(self, container_type: Union[list | dict | str | tuple | None]=None, value:str=None, parent=None):
    self.container_type : Union[list|dict|str|tuple|None] = container_type
    self.value : str = value
    self.parent:ShapeNode = parent
    self.children:list[ShapeNode] = []
    self.tuple_index = None
    self.is_null_val = False

  def get_nullable_container_name(self):
    if self.is_null_val: return f"{self.container_type}?"
    return self.container_type

  def add_child(self, node) -> Self:
    node.parent = self
    self.children.append(node)
    return node

  def has_child_with_container(self, raw_type, out_param:list):
    if self.children is None: return False
    for c in self.children:
      if c.container_type == raw_type:
        out_param.append(c)
        return True

  def has_child_with_value(self, value, tuple_index=None):
    for c in self.children:
      if c.value == value and c.tuple_index == tuple_index:
        return True
    return False

class NodeWriter:
  def __init__(self):
    self.h: Union[ShapeNode | None] = None
    self.current_node: Union[ShapeNode | None] = None

  def pop(self): self.current_node = self.current_node.parent

  def push_container(self, raw_type, tuple_index=None, is_null_val=False):

    new_node = ShapeNode(container_type=raw_type)
    new_node.tuple_index = tuple_index
    new_node.is_null_val = is_null_val

    if self.h is None:
      self.current_node = new_node
      self.h = self.current_node
    else:
      out_param = []
      if self.current_node.has_child_with_container(raw_type, out_param):
        self.current_node = out_param[0]
        if new_node.is_null_val:
          self.current_node.is_null_val = True
        return

      self.current_node = self.current_node.add_child(new_node)

  def push_list(self, tuple_index=None): self.push_container([], tuple_index)
  def push_dict(self, tuple_index=None): self.push_container({}, tuple_index)
  def push_tuple(self, tuple_index=None): self.push_container((1,), tuple_index)
  def push_dict_key(self, key, is_null_val=False): self.push_container(key, tuple_index=None, is_null_val=is_null_val)

  def write_name(self, value, tuple_index=None):
    name = type(value).__name__ if value is not None else "None"
    node = ShapeNode(value=name)
    node.tuple_index = tuple_index
    if self.h is None:
      self.h = node
    else:
      if not self.current_node.has_child_with_value(name, tuple_index):
        self.current_node.add_child(node)

def get_path_to_node_recurse(node):
  yield node.container_type
  if node.parent is not None:
    get_path_to_node_recurse(node.parent)

def get_path_to_node(node):
  return "->".join(list(reversed(get_path_to_node_recurse(node))))

def node_graph_to_obj_dict_key_eval(parent_node:ShapeNode, set_any_type=False) -> Any :
  is_nullable_container = parent_node.is_null_val
  nodes = parent_node.children
  if len(nodes) == 1: return node_graph_to_obj(nodes[0], set_any_type)
  else:
    not_none = lambda x: x is not None
    range_values = list(map(lambda x: x.value, nodes))
    range_containers = list(map(lambda x: x.container_type, nodes))
    values = list(filter(not_none, range_values))
    containers = list(filter(not_none, range_containers))
    has_primitives = any(values)
    has_containers = any(containers)

    if is_nullable_container:
      nodes_without_none_type = list(filter(lambda x: x.container_type is not None, nodes))
      if len(nodes_without_none_type) == 1:
        return node_graph_to_obj(nodes_without_none_type[0], set_any_type)

    if has_primitives and not has_containers:
      if is_nullable_container:
        #when the container is "nullable?", we won't bother specifying None in the property
        return "|".join(values)
      else:
        return "|".join(range_values)

    path = get_path_to_node(nodes[0].parent.parent)
    key = nodes[0].parent
    str_rep = get_path_to_node(nodes[0])

    if has_primitives and has_containers:
      #in the case a dictionary has keys of differing types (other than None),
      #will issue a warning and continue processing with the container
      sys.stderr.writelines(f"WARNING: {path} dictionary key {key} contains both primitives and values: {str_rep}")
      return "|".join(range_values + range_containers)
    elif not has_primitives and has_containers:
      sys.stderr.writelines(f"ERROR: {path} dictionary key {key} contains both array and dictionary accessors: {str_rep}")
      return "|".join(range_containers)
    
    raise Exception("unexpected path")

#NOTE: recurse with nodeGraphToObj_dictKeyEval
def node_graph_to_obj(node:ShapeNode, set_any_type=False) -> Any :
  if node.value is not None:
    if set_any_type:
      return 'Any'
    else:
      return node.value
  if isinstance(node.container_type, dict):
    return {c.get_nullable_container_name(): node_graph_to_obj_dict_key_eval(c, set_any_type) for c in node.children}
  if isinstance(node.container_type, list):
    return [node_graph_to_obj(c, set_any_type) for c in node.children]
  if isinstance(node.container_type, tuple):
    return tuple([node_graph_to_obj(c, set_any_type) for c in sorted(node.children, key=lambda x: x.tuple_index)])
  
  raise Exception("unexpected path")


def dict_kv(obj):
  if isinstance(obj, dict):
    for k in obj:
      yield k, obj[k]
  else:
    v = vars(obj)
    for k in vars(obj).keys():
      yield k, v.get(k)

def normalize_type(obj):
  if hasattr(obj, "__dict__"):
    obj = obj.__dict__
  return obj

def object_crawler(obj, node_writer, tuple_index=None):

  obj = normalize_type(obj)

  if isinstance(obj, list):
    node_writer.push_list(tuple_index)
    for prop in obj:
      object_crawler(prop, node_writer)
    node_writer.pop()
  elif isinstance(obj, dict):
    node_writer.push_dict(tuple_index)
    for (key, value) in dict_kv(obj):
      node_writer.push_dict_key(key, is_null_val=value is None)
      object_crawler(value, node_writer)
      node_writer.pop()
    node_writer.pop()
  elif isinstance(obj, tuple):
    node_writer.push_tuple(tuple_index)
    for i in range(0, len(obj)):
      object_crawler(obj[i], node_writer, tuple_index=i)
    node_writer.pop()
  else:
    node_writer.write_name(obj, tuple_index)

class BaseShape:
  def __init__(self, obj):
    self.obj = obj

  def __eq__(self, other):
    return self.obj == other

  def __repr__(self):
    ss = io.StringIO()
    ss.write("\n")
    pprint.pprint(self.obj, stream=ss, indent=2)
    ss_len = ss.tell()
    ss.seek(0)
    data_str = ss.read(ss_len - 1)
    return data_str

  @staticmethod
  def factory(obj):
    if isinstance(obj, dict): return DictShape(obj)
    if isinstance(obj, list): return ListShape(obj)
    if isinstance(obj, tuple): return TupleShape(obj)
    if isinstance(obj, str): return StrShape(obj)
    return NoneShape()

class NoneShape(BaseShape):
  def __init__(self):
    super().__init__(None)



class DictShape(dict, BaseShape):
  def __init__(self, obj):
    super().__init__(obj)
    self.obj = obj

  def __repr__(self): return BaseShape.__repr__(self)
  
  def __getattr__(self, item):
    if item in self.obj.keys(): return BaseShape.factory(self.obj[item])
    return NoneShape()




class ListShape(list, BaseShape):
  def __init__(self, obj):
    super().__init__(obj)
    self.obj = obj
    
  def __repr__(self): return BaseShape.__repr__(self)

  def __getattr__(self, item):
    if hasattr(self.obj, item): return BaseShape.factory(self.obj[item])
    return NoneShape()

  def __getitem__(self, item):
    return BaseShape.factory(self.obj[item])




class StrShape(str, BaseShape):
  def __init__(self, obj):
    super().__init__(obj)
    self.obj = obj

  def __repr__(self): return BaseShape.__repr__(self)




class TupleShape(BaseShape):
  def __init__(self, obj):
    super().__init__(obj)
    self.obj = obj

  def __repr__(self): return BaseShape.__repr__(self)




def eval_shape(obj:Any, set_any_type=False) -> Any:
  w = NodeWriter()
  object_crawler(obj, w)
  res = node_graph_to_obj(w.h, set_any_type)
  return BaseShape.factory(res)
