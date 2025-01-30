
class distinctGenerator():

  def __init__(self, parent=None):
    self.parent = parent
    self.tracking = set()
    self.buffer = []

  def __iter__(self):
    return self

  def __next__(self):
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

  def __getKey(self):
    return '.'.join(self.currentPath)
  
  def add(self, obj):
    oh = type(obj).__name__
    if not oh in self.h:
      self.h[oh] = distinctGenerator()
  
  def remove(self, obj):
    self.__getKey()

  def iterList(self, xList):
    self.__getKey()
    
  def iterDict(self, xDict):
    self.__getKey()

  def value(self):
    self.__getKey()

  def result(self):
    return self.iterGraph #todo expand
    
def evalShapeWithContext(obj, context):
  isList = isinstance(obj, list)
  isDict = hasattr(obj, "__dict__")

  if isList:
    context.add(obj)
    for prop in context.iterList(obj):
      evalShapeWithContext(prop, context)
  elif isDict:
    context.add(obj)
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



