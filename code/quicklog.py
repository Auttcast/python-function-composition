
enableLogging = False
enableProdWriting = False

def log(message, override=None):
  if enableLogging or override == True:
    print(message)

def tracelog(message, enable=False):
  def funcWrap(func):
    def loggingWrapper(*args, **kargs):
      global enableLogging
      if enable:
        enableLogging = True
      log("\n")
      log(f"START {message}")
      res = func(*args, **kargs)
      log(f"END {message}")
      if enable:
        enableLogging = False
      return res#probably none
    return loggingWrapper
  return funcWrap
