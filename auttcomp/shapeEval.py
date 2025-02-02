from typing import Union, Self, Any
import sys, pprint
from .utility import unwrapFromSingleTuple

class shapeNode:
  def __init__(self, containerType: Union[list|dict|str|tuple|None]=None, value:str=None, parent=None):
    self.containerType : Union[list|dict|str|tuple|None] = containerType
    self.value : str = value
    self.parent:shapeNode = parent
    self.children:[shapeNode] = []

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

  def hasChildWithValue(self, value):
    for c in self.children:
      if c.value == value:
        return True
    return False

class nodeWriter():
  def __init__(self):
    self.h: Union[shapeNode|None] = None
    self.currentNode: Union[shapeNode|None] = None

  def apop(self): self.currentNode = self.currentNode.parent

  def pushContainer(self, rawType):

    newNode = shapeNode(containerType=rawType)

    if self.h is None:
      self.currentNode = newNode
      self.h = self.currentNode
    else:
      outParam = []
      if self.currentNode.hasChildWithContainer(rawType, outParam):
        self.currentNode = outParam[0]
        return

      self.currentNode = self.currentNode.addChild(newNode)

  def pushList(self): self.pushContainer([])
  def pushDict(self): self.pushContainer({})
  def pushTuple(self): self.pushContainer((1,))
  def pushDictKey(self, key): self.pushContainer(key)

  def writeName(self, value):
    name = type(value).__name__
    node = shapeNode(value=name)
    if self.h is None:
      self.h = node
    else:
      if not self.currentNode.hasChildWithValue(name):
        self.currentNode.addChild(node)

def getPathToNodeRecurse(node):
  yield node.containerType
  if node.parent is not None:
    getPathToNodeRecurse(node.parent)

def getPathToNode(node):
  return "->".join(list(reversed(getPathToNodeRecurse(node))))

def nodeGraphToObj_dictKeyEval(nodes:shapeNode, setAnyType=False) -> Any :
  if len(nodes) == 1: return nodeGraphToObj(nodes[0], setAnyType)
  else:
    notNone = lambda x: x is not None
    nodeValues = list(map(lambda x: x.value, nodes))
    nodeCont = list(map(lambda x: x.containerType, nodes))
    values = list(filter(notNone, nodeValues))
    containers = list(filter(notNone, nodeCont))
    hasPrimitives = any(values)
    hasContainers = any(containers)

    if hasPrimitives and not hasContainers:
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
    return {c.containerType: nodeGraphToObj_dictKeyEval(c.children, setAnyType) for c in node.children}
  if isinstance(node.containerType, list):
    return [nodeGraphToObj(c, setAnyType) for c in node.children]
  if isinstance(node.containerType, tuple):
    return tuple([nodeGraphToObj(c, setAnyType) for c in node.children])


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

def objectCrawler(obj, nodeWriter):

  obj = normalizeType(obj)

  if isinstance(obj, list):
    nodeWriter.pushList()
    for prop in obj:
      objectCrawler(prop, nodeWriter)
    nodeWriter.apop()
  elif isinstance(obj, dict):
    nodeWriter.pushDict()
    for (key, value) in dictKv(obj):
      nodeWriter.pushDictKey(key)
      objectCrawler(value, nodeWriter)
      nodeWriter.apop()
    nodeWriter.apop()
  elif isinstance(obj, tuple):
    nodeWriter.pushTuple()
    for item in obj:
      objectCrawler(item, nodeWriter)
    nodeWriter.apop()
  else:
    nodeWriter.writeName(obj)

def evalShape(obj, setAnyType=False):
  w = nodeWriter()
  objectCrawler(obj, w)

  return nodeGraphToObj(w.h, setAnyType)

def printShape(obj, setAnyType=False):
  pprint.pprint(evalShape(obj, setAnyType), indent=2)
