
printTracking = True

class Ghost(object):
  def __init__(self):
    super().__init__()
    self.tracking = []

  def __getattr__(self, name):
    self.tracking.append(name)
    return self

