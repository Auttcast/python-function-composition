import asyncio
import pytest
import threading
from ..extensions import Api as f
from typing import Any, AsyncGenerator
from ..async_context import AsyncContext

@pytest.mark.asyncio
async def test_source_adapter_returns_gen():

    data = [1, 2, 3]

    async def get_gen(data):
        for d in data:
            yield d

    def get_iter(data):
        for d in data:
            yield d

    async def assert_gen_of_data(result_gen):

        assert isinstance(result_gen, AsyncGenerator)

        result_data = []
        async for x in result_gen:
            result_data.append(await x)

        assert result_data == data

    await assert_gen_of_data(await AsyncContext.source_adapter(data))
    await assert_gen_of_data(await AsyncContext.source_adapter(get_gen(data)))
    await assert_gen_of_data(await AsyncContext.source_adapter(get_iter(data)))

@pytest.mark.asyncio
async def test_async_map_io_and_cpu_bound():

    '''
    depending on thread contention, cpu_bound_tids may equal 1 when few items exist in the set
    to increase probability that more than one thread will be involved, data with range of 10 is used
    '''

    data = list(range(0, 10))

    sync_lock = threading.Lock()
    cpu_bound_tids = []
    def cpu_bound(x):
        with sync_lock:
            cpu_bound_tids.append(threading.get_ident())
        return x+1

    async_lock = asyncio.Lock()
    io_bound_tids = []
    async def io_bound(x):
        async with async_lock:
            io_bound_tids.append(threading.get_ident())        
        return x+1

    comp = AsyncContext()(lambda f: (
        f.map(cpu_bound)
        | f.map(io_bound)
        | f.list
    ))

    result = await comp(data)
    assert result == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    assert len(set(io_bound_tids)) == 1
    assert len(set(cpu_bound_tids)) > 1

@pytest.mark.asyncio
async def test_async_map():

    async def inc_async(x):
        return x + 1
    
    def inc_sync(x):
        return x + 1
    
    data = [1, 2, 3]

    async_comp = AsyncContext()(lambda f: (
        f.map(inc_async)
        | f.map(inc_sync)
        | f.list
    ))

    result = await async_comp(data)

    assert result == [3, 4, 5]


@pytest.mark.asyncio
async def test_async_filter():
    
    data = [1, 2, 3]

    async def filter_async(x):
        return x > 1
    
    def filter_sync(x):
        return x > 2
    
    async_comp = AsyncContext()(lambda f: (
        f.filter(filter_async)
        | f.filter(filter_sync)
        | f.list
    ))

    result = await async_comp(data)

    assert result == [3]


@pytest.mark.asyncio
async def test_async_flatmap():

    async def select_async(x):
        return x
    
    def select_sync(x):
        return x
    
    data = [[1], [2], [3]]

    async_result = await (f.id(data) > AsyncContext()(lambda f: (
        f.flatmap(select_async)
        | f.list
    )))

    sync_result = await (f.id(data) > AsyncContext()(lambda f: (
        f.flatmap(select_sync)
        | f.list
    )))

    assert async_result == [1, 2, 3]
    assert sync_result == [1, 2, 3]

