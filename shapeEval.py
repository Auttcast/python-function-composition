
class distinctGenerator():
  #stop generating when parent object
  keys = {}

  #def __init__(self, ):

  def __iter__(self): 
    return self

  def __next__(self):
    if self.start >= self.stop:
      raise StopIteration
      current = self.start * self.start
      self.start += 1
    return current

  #def receiveData(data):
  

class deepYield():
  
  keyCont = []#'dict.prop.list.dict.prop
  
  def getKey(self):
    return '.'.join(keyCont)
  
  def add(self, obj):
    oh = type(obj).__name__
    if not oh in self.h:
      self.h[oh] = distinctGenerator()
  
 # def remove(self, obj):
    
  
  def __init__(self):
    self.h = {}
  
  def iterList(self, xList):
    self.getKey()
    
  def iterDict(self, xDict):
    self.getKey()
    
def evalShapeWithContext(obj, context):
  r = None
  
  isList = isinstance(obj, list)
  isDict = hasattr(obj, "__dict__")
  
  moveContext = isList or isDict
  if moveContext: context.add(obj)
  
  if isList:
    r = []
    for prop in context.iterList(obj):
      p = evalShapeWithContext(prop, context)
      r.append(p)
  elif isDict:
    v = vars(obj)
    r = {k: evalShapeWithContext(v.get(k), context) for k in context.iterDict(list(v.keys()))}
  else:
    r = type(obj).__name__
  
  if moveContext: context.remove(obj)
  
  return r
  
def __evalShape(obj):
  if isinstance(obj, list):
    r = []
    for prop in obj:
      p = __evalShape(prop)
      if p not in r:
        r.append(p)
    return r
  elif hasattr(obj, "__dict__"):
    v = vars(obj)
    r = {k: __evalShape(v.get(k)) for k in v.keys()}
  else:
    return type(obj).__name__

def evalShape(obj):
  dy = deepYield()
  context = evalShapeWithContext(obj, dy)
  return __evalShape(obj)



