import concurrent.futures
from auttcomp.async_context import AsyncContext
import asyncio
import concurrent
'''
----------------------------------------------------------------------------------------- benchmark: 4 tests ----------------------------------------------------------------------------------------
Name (time in ms)                   Min                 Max                Mean             StdDev              Median                IQR            Outliers       OPS            Rounds  Iterations
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_io_bound_processpool        2.2557 (1.0)        5.7642 (1.03)       2.7635 (1.0)       0.9503 (1.10)       2.3202 (1.0)       0.1471 (1.0)         24;46  361.8634 (1.0)         205           1
test_io_bound_async              2.2695 (1.01)       5.5740 (1.0)        2.7771 (1.00)      0.8607 (1.0)        2.3505 (1.01)      0.4771 (3.24)        24;24  360.0938 (1.00)        209           1
test_cpu_bound_async            49.5825 (21.98)     73.1695 (13.13)     62.5791 (22.65)     7.9837 (9.28)      64.6472 (27.86)    12.4999 (84.98)         7;0   15.9798 (0.04)         16           1
test_cpu_bound_processpool     230.6250 (102.24)   261.6855 (46.95)    247.6196 (89.60)    13.5633 (15.76)    243.5497 (104.97)   23.0670 (156.82)        3;0    4.0385 (0.01)          5           1
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''


cpu_bound_data = list(range(0, 1000))
def inc_sync(x):
    return x+1

io_bound_data = list(range(0, 1000))
async def inc_async(x):
    return x+1

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
