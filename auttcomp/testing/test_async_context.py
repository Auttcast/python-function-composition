import threading
from typing import Any, AsyncGenerator
from ..async_context import AsyncContext
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async_comp():

    async def inc_async(x):
        return x + 1
    
    data = [2, 1, 1, 1, 1, 2, 2]

    async_comp = AsyncContext()(lambda f: (
        f.map(inc_async)
        | f.map(lambda x: x+1)
        | f.filter(lambda x: x != 3)
        | f.map(inc_async)
        | f.list
    ))

    result = await async_comp(data)

    assert result == [5, 5, 5]


@pytest.mark.asyncio
async def test_async_comp_return_gen():
    
    async def inc_async(x):
        return x + 1
    
    data = [2, 1, 1, 1, 1, 2, 2]

    async_comp = AsyncContext()(lambda f: (
        f.map(inc_async)
        | f.map(lambda x: x+1)
        | f.filter(lambda x: x != 3)
        | f.map(inc_async)
    ))

    result = []
    async for x in await async_comp(data):
        result.append(x)

    assert result == [5, 5, 5]


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

    data = [1, 2, 3]

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
        | f.map(cpu_bound)
        | f.map(io_bound)
        | f.list
    ))

    result = await comp(data)
    assert result == [5, 6, 7]

    assert len(set(io_bound_tids)) == 1
    assert len(set(cpu_bound_tids)) > 1
    
@pytest.mark.asyncio
async def test_async_map_with_exception_handling():

    '''
    implement some form of generic handling?
    user may implement their own handling

    what about timeout or token integration?

    '''

    data = [1, 2, 3]

    def cpu_bound(x):
        if x == 3:
            raise ValueError(f"failed on {x}")
        return x+1

    async def io_bound(x):
        return x+1

    comp = AsyncContext()(lambda f: (
        f.map(cpu_bound)
        | f.map(io_bound)
        | f.map(cpu_bound)
        | f.map(io_bound)
        | f.list
    ))

    result = await comp(data)
    assert result == [5, 6, 7]
