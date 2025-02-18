from typing import Union, Self, Any
import sys, pprint
import io
from .quicklog import log

enableShapeLogging = False


class shapeNode:
  def __init__(self, containerType: Union[list|dict|str|tuple|None]=None, value:str=None, parent=None):
    self.containerType : Union[list|dict|str|tuple|None] = containerType
    self.value : str = value
    self.parent:shapeNode = parent
    self.children:[shapeNode] = []
    self.tupleIndex = None
    self.isNullVal = False

  def getNullableContainerName(self):
    if self.isNullVal: return f"{self.containerType}?"
    return self.containerType

  def addChild(self, node) -> Self:
    node.parent = self
    self.children.append(node)
    return node

  def hasChildWithContainer(self, rawType, outParam:list):
    if self.children is None: return False
    for c in self.children:
      if c.containerType == rawType:
        outParam.append(c)
        return True

  def hasChildWithValue(self, value, tupleIndex=None):
    for c in self.children:
      if c.value == value and c.tupleIndex == tupleIndex:
        return True
    return False

class nodeWriter():
  def __init__(self):
    self.h: Union[shapeNode|None] = None
    self.currentNode: Union[shapeNode|None] = None

  def apop(self): self.currentNode = self.currentNode.parent

  def pushContainer(self, rawType, tupleIndex=None, isNullVal=False):

    newNode = shapeNode(containerType=rawType)
    newNode.tupleIndex = tupleIndex
    newNode.isNullVal = isNullVal

    if self.h is None:
      self.currentNode = newNode
      self.h = self.currentNode
    else:
      outParam = []
      if self.currentNode.hasChildWithContainer(rawType, outParam):
        self.currentNode = outParam[0]
        if newNode.isNullVal:
          self.currentNode.isNullVal = True
        return

      self.currentNode = self.currentNode.addChild(newNode)

  def pushList(self, tupleIndex=None): self.pushContainer([], tupleIndex)
  def pushDict(self, tupleIndex=None): self.pushContainer({}, tupleIndex)
  def pushTuple(self, tupleIndex=None): self.pushContainer((1,), tupleIndex)
  def pushDictKey(self, key, isNullVal=False): self.pushContainer(key, tupleIndex=None, isNullVal=isNullVal)

  def writeName(self, value, tupleIndex=None):
    name = type(value).__name__ if value is not None else "None"
    node = shapeNode(value=name)
    node.tupleIndex = tupleIndex
    if self.h is None:
      self.h = node
    else:
      if not self.currentNode.hasChildWithValue(name, tupleIndex):
        self.currentNode.addChild(node)

def getPathToNodeRecurse(node):
  yield node.containerType
  if node.parent is not None:
    getPathToNodeRecurse(node.parent)

def getPathToNode(node):
  return "->".join(list(reversed(getPathToNodeRecurse(node))))

def nodeGraphToObj_dictKeyEval(parentNode:shapeNode, setAnyType=False) -> Any :
  isNullableContainer = parentNode.isNullVal
  nodes = parentNode.children
  if len(nodes) == 1: return nodeGraphToObj(nodes[0], setAnyType)
  else:
    notNone = lambda x: x is not None
    nodeValues = list(map(lambda x: x.value, nodes))
    nodeCont = list(map(lambda x: x.containerType, nodes))
    values = list(filter(notNone, nodeValues))
    containers = list(filter(notNone, nodeCont))
    hasPrimitives = any(values)
    hasContainers = any(containers)

    if isNullableContainer:
      nodesWithoutNoneType = list(filter(lambda x: x.containerType is not None, nodes))
      if len(nodesWithoutNoneType) == 1:
        return nodeGraphToObj(nodesWithoutNoneType[0], setAnyType)

    if hasPrimitives and not hasContainers:
      if isNullableContainer:
        #when the container is "nullable?", we won't bother specifying None in the property
        vals = list(filter(lambda x: x is not None, nodeValues))
        return "|".join(vals)
      else:
        return "|".join(nodeValues)

    path = getPathToNode(nodes[0].parent.parent)
    key = nodes[0].parent
    strRep = getPathToNode(nodes[0])

    if hasPrimitives and hasContainers:
      #in the case a dictionary has keys of differing types (other than None),
      #will issue a warning and continue processing with the container
      sys.stderr.writelines(f"WARNING: {path} dictionary key {key} contains both primitives and values: {strRep}")
      return "|".join(nodeValues + nodeCont)
    elif not hasPrimitives and hasContainers:
      sys.stderr.writelines(f"ERROR: {path} dictionary key {key} contains both array and dictionary accessors: {strRep}")
      return "|".join(nodeCont)

#NOTE: recurse with nodeGraphToObj_dictKeyEval
def nodeGraphToObj(node:shapeNode, setAnyType=False) -> Any :
  if node.value is not None:
    if setAnyType:
      return 'Any'
    else:
      return node.value
  if isinstance(node.containerType, dict):
    return {c.getNullableContainerName(): nodeGraphToObj_dictKeyEval(c, setAnyType) for c in node.children}
  if isinstance(node.containerType, list):
    return [nodeGraphToObj(c, setAnyType) for c in node.children]
  if isinstance(node.containerType, tuple):
    return tuple([nodeGraphToObj(c, setAnyType) for c in sorted(node.children, key=lambda x: x.tupleIndex)])


def dictKv(obj):
  if isinstance(obj, dict):
    for k in obj:
      yield (k, obj[k])
  else:
    v = vars(obj)
    for k in vars(obj).keys():
      yield (k, v.get(k))

def normalizeType(obj):
  if hasattr(obj, "__dict__"):
    obj = obj.__dict__
  return obj

def objectCrawler(obj, nodeWriter, tupleIndex=None):

  obj = normalizeType(obj)

  if isinstance(obj, list):
    nodeWriter.pushList(tupleIndex)
    for prop in obj:
      objectCrawler(prop, nodeWriter)
    nodeWriter.apop()
  elif isinstance(obj, dict):
    nodeWriter.pushDict(tupleIndex)
    for (key, value) in dictKv(obj):
      nodeWriter.pushDictKey(key, isNullVal=value is None)
      objectCrawler(value, nodeWriter)
      nodeWriter.apop()
    nodeWriter.apop()
  elif isinstance(obj, tuple):
    nodeWriter.pushTuple(tupleIndex)
    for i in range(0, len(obj)):
      objectCrawler(obj[i], nodeWriter, tupleIndex=i)
    nodeWriter.apop()
  else:
    nodeWriter.writeName(obj, tupleIndex)

class BaseShape:
  def __init__(self, obj):
    self.obj = obj

  def __eq__(self, other):
    return self.obj == other

  def __repr__(self):
    ss = io.StringIO()
    ss.write("\n")
    pprint.pprint(self.obj, stream=ss, indent=2)
    ssLen = ss.tell()
    ss.seek(0)
    dataStr = ss.read(ssLen - 1)
    if enableShapeLogging:
      print(dataStr)
    return dataStr

  @staticmethod
  def Factory(obj):
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
    if item in self.obj.keys(): return BaseShape.Factory(self.obj[item])
    return NoneShape()




class ListShape(list, BaseShape):
  def __init__(self, obj):
    super().__init__(obj)
    self.obj = obj
    
  def __repr__(self): return BaseShape.__repr__(self)

  def __getattr__(self, item):
    if hasattr(self.obj, item): return BaseShape.Factory(self.obj[item])
    return NoneShape()

  def __getitem__(self, item):
    return BaseShape.Factory(self.obj[item])




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




def evalShape(obj, setAnyType=False):
  w = nodeWriter()
  objectCrawler(obj, w)
  res = nodeGraphToObj(w.h, setAnyType)
  return BaseShape.Factory(res)
