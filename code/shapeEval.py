
class distinctGenerator():

  def __init__(self, parent=None):
    self.parent = parent
    self.tracking = set()
    self.buffer = []

  def __iter__(self):
    return iter(self.buffer)

  def send(self, data):
    for d in data:
      if d not in self.tracking:
        self.tracking.add(d)
        self.buffer.append(d)

  #def receiveData(data):
  
#matches a distinctGenerator with document path
class deepYield():

  def __init__(self):
    self.h = {} # {path: distinctGenerator}
    self.currentPath = []#'dict.prop.list.dict.prop
    self.iterGraph = None
    self.graphSetter = None

  def __getKey(self):
    return '.'.join(self.currentPath)

  def dictSetter(self, k, v):

    self.currentPath.append('set')
    self.iterGraph[k] = v

  def listSetter(self, x):
    self.currentPath.append('list')
    self.iterGraph.append(x)

  def __addDict(self, key, value):
    if self.iterGraph is None:
      self.iterGraph = dict()
      self.graphSetter = self.dictSetter
    else:
      #use setter of parent object
      self.graphSetter(dict())


  def __addList(self, obj):
    if self.iterGraph is None:
      self.iterGraph = []
    else:
      #use setter of parent object
      self.graphSetter([])

    self.graphSetter = lambda g, x: g.append(x)
    oh = self.__getKey()
    if not oh in self.h:
      self.h[oh] = distinctGenerator()
  
  def remove(self, obj):
    self.__getKey()

  def iterList(self, xList):
    self.__addList([])
    for x in xList:
      yield x
    
  def iterDict(self, xDict):
    self.__getKey()
    for x in xDict:
#      self.add(
      yield x

  def value(self, v):

    if self.iterGraph == None:
      #no context was set and the structure is simply this.
      self.iterGraph = type(v).__name__

    #todo send name to the current generator
    #update graphe

  def result(self):
    return self.iterGraph #todo expand

#desire to seperate creation of structure from hierarchy
class deepYield2():

  def iterList(self):


def evalShapeWithContext2(obj, context):
  isList = isinstance(obj, list)
  isDict = hasattr(obj, "__dict__")

  if isList:
    for prop in context.iterList(obj):
      evalShapeWithContext(prop, context)
  elif isDict:
    v = vars(obj)
    for k in context.iterDict(list(v.keys())):
      evalShapeWithContext(v.get(k), context)
    context.remove(obj)
  else:
    context.value(type(obj).__name__)

def evalShapeWithContext(obj, context):
  isList = isinstance(obj, list)
  isDict = hasattr(obj, "__dict__")

  if isList:
    for prop in context.iterList(obj):
      evalShapeWithContext(prop, context)
  elif isDict:
    v = vars(obj)
    for k in context.iterDict(list(v.keys())):
      evalShapeWithContext(v.get(k), context)
    context.remove(obj)
  else:
    context.value(type(obj).__name__)


def evalShape(obj):
  dy = deepYield()
  evalShapeWithContext(obj, dy)
  dy.result()



