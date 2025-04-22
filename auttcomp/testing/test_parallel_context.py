import asyncio
import time
from ..parallel_context import ParallelContext
from ..extensions import Api as f

def test_parallel_list_result():

    '''
    ParallelContext is now just a wrapper for AsyncContext executed with asyncio.run
    '''

    def sync_func(x):
        #time.sleep(1)
        return x + 1
    
    async def async_func(x):
        #await asyncio.sleep(1)
        return x + 1

    data = [1, 2, 3]

    comp = ParallelContext()(lambda f: (
        f.map(sync_func)
        | f.map(async_func)
        | f.map(sync_func)
        | f.map(async_func)
        | f.list
    ))

    result = comp(data)

    assert result == [5, 6, 7]

def test_parallel_iter_result():

    '''
    ParallelContext's exit_boundary is implemented to return a list when the result type is async_gen
    because naturally, async_gen can not be practically evaluated outside of the async environment
    '''

    def sync_func(x):
        #time.sleep(1)
        return x + 1
    
    async def async_func(x):
        #await asyncio.sleep(1)
        return x + 1

    data = [1, 2, 3]

    comp = ParallelContext()(lambda f: (
        f.map(sync_func)
        | f.map(async_func)
        | f.map(sync_func)
        | f.map(async_func)
    ))

    result = comp(data)

    assert result == [5, 6, 7]
