import concurrent.futures
from auttcomp.async_context import AsyncContext, ExecutionType
from auttcomp.parallel_context import ParallelContext
from ..extensions import Api as f
import asyncio
import pytest
import time
import concurrent
import uvloop
'''

NOTES


-------------------------------------------------------------------------------------- benchmark: 5 tests -------------------------------------------------------------------------------------
Name (time in ms)                Min                 Max                Mean            StdDev              Median               IQR            Outliers      OPS            Rounds  Iterations
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_async_io_bound          30.8668 (1.0)       31.3776 (1.00)      31.0445 (1.0)      0.0968 (1.0)       31.0317 (1.00)     0.0977 (1.0)           5;2  32.2118 (1.0)          33           1
test_parallel_io_bound       30.9094 (1.00)      31.3304 (1.0)       31.0652 (1.00)     0.1198 (1.24)      31.0217 (1.0)      0.1835 (1.88)         13;0  32.1903 (1.00)         33           1
test_async_cpu_bound         32.3815 (1.05)      39.0766 (1.25)      33.0200 (1.06)     1.1664 (12.04)     32.8583 (1.06)     0.3113 (3.19)          1;1  30.2847 (0.94)         30           1
test_parallel_cpu_bound      32.4972 (1.05)      33.1523 (1.06)      32.7964 (1.06)     0.1776 (1.83)      32.7472 (1.06)     0.2820 (2.89)          8;0  30.4911 (0.95)         29           1
test_iter                   304.3560 (9.86)     304.8425 (9.73)     304.6557 (9.81)     0.1861 (1.92)     304.7300 (9.82)     0.2142 (2.19)          2;0   3.2824 (0.10)          5           1
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''


cpu_bound_data = list(range(0, 1000))
def inc_sync(x):
    #time.sleep(0.01)
    return x+1

io_bound_data = list(range(0, 1000))
async def inc_async(x):
    #await asyncio.sleep(0.01)
    return x+1

#@pytest.mark.asyncio
def test_cpu_bound_async(benchmark):
    
    async def setup():
        asyncio.set_event_loop(asyncio.new_event_loop())

        comp = AsyncContext()(lambda f:
            f.map(inc_sync)
            | f.map(inc_sync)
            | f.map(inc_sync)
            | f.list
        )
        
        await comp(cpu_bound_data)

    benchmark(lambda: asyncio.run(setup()))


#@pytest.mark.asyncio
def test_io_bound_async(benchmark):
    
    async def setup():
        asyncio.set_event_loop(asyncio.new_event_loop())

        comp = AsyncContext()(lambda f:
            f.map(inc_async)
            | f.map(inc_async)
            | f.map(inc_async)
            | f.list
        )

        await comp(io_bound_data)

    benchmark(lambda: asyncio.run(setup()))


def test_cpu_bound_uvloop(benchmark):
    
    async def setup():

        comp = AsyncContext()(lambda f:
            f.map(inc_sync)
            | f.map(inc_sync)
            | f.map(inc_sync)
            | f.list
        )
        
        await comp(cpu_bound_data)

    benchmark(lambda: uvloop.run(setup()))


def test_io_bound_uvloop(benchmark):
    
    async def setup():

        comp = AsyncContext()(lambda f:
            f.map(inc_async)
            | f.map(inc_async)
            | f.map(inc_async)
            | f.list
        )

        await comp(io_bound_data)

    benchmark(lambda: uvloop.run(setup()))


def test_cpu_bound_processpool(benchmark):
    
    with concurrent.futures.ProcessPoolExecutor() as pool:

        async def setup():

            comp = AsyncContext(cpu_bound_executor=pool)(lambda f:
                f.map(inc_sync)
                | f.map(inc_sync)
                | f.map(inc_sync)
                | f.list
            )
            
            await comp(cpu_bound_data)

        benchmark(lambda: asyncio.run(setup()))


def test_io_bound_processpool(benchmark):
    
    with concurrent.futures.ProcessPoolExecutor() as pool:

        async def setup():

            comp = AsyncContext(cpu_bound_executor=pool)(lambda f:
                f.map(inc_async)
                | f.map(inc_async)
                | f.map(inc_async)
                | f.list
            )

            await comp(io_bound_data)

        benchmark(lambda: asyncio.run(setup()))

@pytest.mark.asyncio
async def test_demo_pool():

    el = asyncio.new_event_loop()
    

def test_demo_pool2():

    '''
    
    in async main
    create an additional loop
    tasks added to additional loop are cancelled after a time limit
    if cancelled, are deferred to main loop
    
    '''

    from concurrent.futures import _base
    from concurrent.futures.thread import BrokenThreadPool, _global_shutdown_lock, _shutdown, _WorkItem

    class CustomThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
        def __init__(self):
            super().__init__()

        #overloaded
        def submit(self, fn, /, *args, **kwargs):
            print(f"self._threads: {len(self._threads)} self._idle_semaphore {self._idle_semaphore._value}")
            with self._shutdown_lock, _global_shutdown_lock:
                if self._broken:
                    raise BrokenThreadPool(self._broken)

                if self._shutdown:
                    raise RuntimeError('cannot schedule new futures after shutdown')
                if _shutdown:
                    raise RuntimeError('cannot schedule new futures after '
                                    'interpreter shutdown')

                f = _base.Future()
                w = _WorkItem(f, fn, args, kwargs)

                self._work_queue.put(w)

                if len(self._threads) < 1:
                    self._adjust_thread_count()

                #self._adjust_thread_count()

                return f

    data = list(range(0, 100))
    context = ParallelContext(cpu_bound_executor=CustomThreadPoolExecutor())

    start = time.time()
    r = f.id(data) > context(lambda f: (
        f.map(lambda x: x+1)
        | f.list
    ))
    end = time.time()

    print(f"duration: {end - start} result len: {len(r)}")