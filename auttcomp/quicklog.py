enableLogging = False
enableProdWriting = True

prefix = ""

def log(message, override=None):
  message = str(message)
  if enableLogging or override == True:
    print(prefix + message)

def tracelog(message, enable=False):
  message = str(message)
  def funcWrap(func):
    def loggingWrapper(*args, **kargs):
      global prefix
      global enableLogging
      if enable:
        enableLogging = True
      try:
        log("\n")
        log(f"START {message}")
        prefix = f"{message} "
        func(*args, **kargs)
        prefix = ""
        log(f"END {message}")
        return
      finally:
        if enable:
          enableLogging = False
    return loggingWrapper
  return funcWrap
