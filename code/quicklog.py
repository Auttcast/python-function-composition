
enableLogging = False
enableProdWriting = False

def log(message):
  if enableLogging:
    print(message)

def tracelog(message):
  def funcWrap(func):
    def loggingWrapper(*args, **kargs):
      log(f"START {message}")
      res = func(*args, **kargs)
      log(f"END {message}")
      return res#probably none
    return loggingWrapper
  return funcWrap
