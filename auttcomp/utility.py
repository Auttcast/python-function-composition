from typing import Iterable

class ObjUtil:

    @staticmethod
    def exec_generator(gen):
        if isinstance(gen, dict):
            #note dict is iterable
            return gen
        if isinstance(gen, Iterable):
            return list(gen)
        else: return gen
