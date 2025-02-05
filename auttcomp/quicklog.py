import sys

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

def source(frame):
  target = frame.f_back.f_back.f_locals
  if isinstance(target, dict) and 'self' in target.keys() and isinstance(target['self'], object):
    return target['self'].__class__.__qualname__
  else:
    return f"global"

def logFactory(enabled, prefix=""):
  def invoke(message):
    if enabled:
      sourceClass = source(sys._getframe())
      scm = f"[{ sourceClass }]"
      bold = f"{ConsoleColor.BOLD}" if sourceClass == "global" else ""
      wholePrefix = f"{ConsoleColor.CYAN}{prefix} {bold}{scm}".ljust(30, " ")
      col = ConsoleColor.CYAN + bold
      print(f"\n{col}{wholePrefix}{len(col) * " "} > {ConsoleColor.END} {str(message)}", end="")
  return invoke

logProxy = logFactory(False)

def log(message):
  logProxy(message)

def tracelog(prefix, enable=False):
  def funcWrap(func):
    def loggingWrapper(*args, **kargs):
      global logProxy
      logProxy = logFactory(enable, prefix)
      logProxy(f"{ConsoleColor.GREEN}START{ConsoleColor.END}")
      try:
        func(*args, **kargs)
      finally:
        logProxy(f"{ConsoleColor.GREEN}END{ConsoleColor.END}")
    return loggingWrapper
  return funcWrap
