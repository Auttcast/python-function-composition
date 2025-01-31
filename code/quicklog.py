import functools

enableLogging = False
enableProdWriting = False

prefix = ""

def log(message, override=None):
  if enableLogging or override == True:
    print(prefix + message)

def tracelog(message, enable=False):
  def funcWrap(func):
    @functools.wraps(func)
    def loggingWrapper(*args, **kargs):
      global prefix
      global enableLogging
      if enable:
        enableLogging = True
      log("\n")
      log(f"START {message}")
      prefix = f"{message} "
      res = func(*args, **kargs)
      prefix = ""
      log(f"END {message}")
      if enable:
        enableLogging = False
      return res#probably none
    return loggingWrapper
  return funcWrap
