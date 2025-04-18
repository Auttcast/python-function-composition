from concurrent.futures import ThreadPoolExecutor
from ..parallel_context import ParallelContext
from ..extensions import Api as f
import time

def xtest_exp_parallel():

    '''
    todo
    swap sleep with parallel confirmation
    expand api
    '''

    def blocking_callback(x):
        time.sleep(1)
        return x + 1
    
    def blocking_is_even(x):
        time.sleep(1)
        return x % 2 == 0

    data = [1, 2, 3]
        
    with ThreadPoolExecutor() as pool:

        result = f.id(data) > ParallelContext(pool)(lambda f: (
            f.map(blocking_callback) 
            | f.map(blocking_callback)
            | f.map(blocking_callback)
            | f.filter(blocking_is_even)
            | f.list
        ))

        print(result)
