enableLogging = False
enableProdWriting = True

prefix = ""

class ConsoleColor:
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  GREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'


def log(message, override=None):
  message = str(message)
  if enableLogging or override == True:
    print(f"{ConsoleColor.CYAN}{prefix}{ConsoleColor.END}{message}")

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
