import time
from auttcomp.async_context import AsyncContext
from auttcomp.parallel_context import ParallelContext
from ..extensions import Api as f
import asyncio
import pytest

'''
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

data = list(range(0, 10))
expected = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

def inc_sync(x):
    time.sleep(0.01)
    return x+1

async def inc_async(x):
    await asyncio.sleep(0.01)
    return x+1

def test_iter(benchmark):
    def setup():
        comp = (
            f.map(inc_sync)
            | f.map(inc_sync)
            | f.map(inc_sync)
            | f.list
        )

        assert comp(data) == expected

    benchmark(setup)

def test_parallel_cpu_bound(benchmark):
    def setup():
        comp = ParallelContext()(lambda f:
            f.map(inc_sync)
            | f.map(inc_sync)
            | f.map(inc_sync)
            | f.list
        )
        assert comp(data) == expected

    benchmark(setup)

def test_parallel_io_bound(benchmark):
    def setup():
        comp = ParallelContext()(lambda f:
            f.map(inc_async)
            | f.map(inc_async)
            | f.map(inc_async)
            | f.list
        )

        assert comp(data) == expected

    benchmark(setup)

#@pytest.mark.asyncio
def test_async_cpu_bound(benchmark):
    
    async def setup():
        asyncio.set_event_loop(asyncio.new_event_loop())

        comp = AsyncContext()(lambda f:
            f.map(inc_sync)
            | f.map(inc_sync)
            | f.map(inc_sync)
            | f.list
        )
        
        assert await comp(data) == expected

    def main():
        asyncio.run(setup())

    benchmark(main)

#@pytest.mark.asyncio
def test_async_io_bound(benchmark):
    
    async def setup():
        asyncio.set_event_loop(asyncio.new_event_loop())

        comp = AsyncContext()(lambda f:
            f.map(inc_async)
            | f.map(inc_async)
            | f.map(inc_async)
            | f.list
        )

        assert await comp(data) == expected

    def main():
        asyncio.run(setup())

    benchmark(main)
