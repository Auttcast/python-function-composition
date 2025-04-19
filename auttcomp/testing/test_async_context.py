from typing import Any, AsyncGenerator
from ..async_context import AsyncContext, AsyncUtil
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async_coerce():

    def t_func(x):
        return x+1
    
    async def t_async_func(x):
        return x+1

    async def t_async_func_await(x):
        return await asyncio.sleep(0, x+1)

    co_func1 = AsyncUtil.coerce_async(lambda x: x+1)
    co_func2 = AsyncUtil.coerce_async(t_func)
    co_func3 = AsyncUtil.coerce_async(t_async_func)
    co_func4 = AsyncUtil.coerce_async(t_async_func_await)

    r1 = await co_func1(1)
    r2 = await co_func2(1)
    r3 = await co_func3(1)
    r4 = await co_func4(1)

    assert r1 == 2
    assert r2 == 2
    assert r3 == 2
    assert r4 == 2

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

