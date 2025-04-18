import inspect
import time
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Iterable, Union
from auttcomp.async_composable import AsyncComposable
from ..extensions import Api as f
import asyncio
import pytest

class AsyncUtil:

    @staticmethod
    async def eager_boundary[T](source_gen:AsyncGenerator[Any, T]) -> AsyncGenerator[Any, T]:

        running = []
        async for d in source_gen:
            running.append(asyncio.create_task(d))

        for r in running:
            yield await r
        
    @staticmethod            
    async def value_co(value):
        return value
    
    @staticmethod
    def as_async(func):
        async def co_func(*args):
            return func(*args)
        return co_func

    @staticmethod
    def coerce_async(func):
        if inspect.iscoroutinefunction(func):
            return func
        else:
            return AsyncUtil.as_async(func)

class AsyncApi:

    '''
    AsyncApi for IO, ParallelApi for CPU

    Pattern to optimize for parallelism and eager execution:
    -eager execution is possible thru a series of consecutive maps, 
    in which case, every map func is treated as a continuation of the iterable/gen 
    source and will continue this pattern until a function with eager_boundary is encountered
    
    reinforce a best practice: when async is used, everything should be async.
    -not going to worry about async-sync type of issues here, except for lambdas

    todo:
    -bug fix missing f.list
    -if AsyncContext returns Iterable then implement eager exec
    
    '''

    @staticmethod
    async def __co_map_exec(co_func, co):
        return await co_func(await co)

    def map[T, R](self, func:Callable[[T], R]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, R]]:
        
        func = AsyncUtil.coerce_async(func)

        @AsyncComposable
        async def partial_map(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[R]]:
            async for co in source_gen:
                yield AsyncApi.__co_map_exec(func, co)
                
        return partial_map

    def filter[T](self, func:Callable[[T], bool]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, T]]:

        func = AsyncUtil.coerce_async(func)

        @AsyncComposable
        async def partial_filter(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[T]]:
            async for value in AsyncUtil.eager_boundary(source_gen):
                if await func(value):
                    yield AsyncUtil.value_co(value)
                
        return partial_filter

    @AsyncComposable
    async def list[T](source_gen:AsyncGenerator[Any, Awaitable[T]]) -> list[T]:
        results = []        
        async for d in AsyncUtil.eager_boundary(source_gen):
            results.append(d)
        return results

class AsyncContext:

    @staticmethod
    @AsyncComposable
    async def source_adapter[T](data:Union[AsyncGenerator[Any, T] | Iterable[T]]) -> AsyncGenerator[Any, T]:
        
        if isinstance(data, Iterable):
            for x in data:
                yield AsyncUtil.value_co(x)
        elif isinstance(data, AsyncGenerator):
            async for x in data:
                if isinstance(x, Coroutine):
                    yield x
                else:
                    yield AsyncUtil.value_co(x)
        else:
            raise TypeError(f"data type {type(data)} not supported")

    def __call__(self, composition_factory:Callable[[AsyncApi], AsyncComposable]) -> AsyncComposable:
        '''
        todo
        composition bug?
        return async_gen eager exec
        '''
        return AsyncContext.source_adapter | composition_factory(AsyncApi())

@pytest.mark.asyncio
async def test_comp_w_id_invoke():

    @AsyncComposable
    async def test_func(x:int) -> int:
        await asyncio.sleep(0)
        return x+1

    comp = test_func | test_func | test_func

    r = await (f.id(1) > comp)

    assert r == 4

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
async def test_map_ext():

    async def inc_async(x):
        await asyncio.sleep(1)
        return x + 1
    
    data = [2, 1, 1, 1, 1, 2, 2, 2]

    async_comp = AsyncContext()(lambda f: (
        f.map(inc_async)
        | f.map(inc_async)
        | f.filter(lambda x: x != 3)
        | f.map(inc_async)
        | f.list
        | f.list
    ))

    start_time = time.time()
    result = await async_comp(data)
    end_time = time.time()
    print(f"duration: {end_time - start_time}")
    print(result)


@pytest.mark.asyncio
async def test_comp_debug():

    '''
    prepending to comp?
    '''

    api = AsyncApi()

    class MiniCompose:
        def __call__(self, cb):
            
            #return AsyncContext.source_adapter | cb(AsyncApi())
            return cb(AsyncApi())
        
    comp = MiniCompose()(lambda f: (
        f.map(lambda x: x+1) 
        | f.map(lambda x: x+1) 
        | f.list
    ))

    async def get_gen(data):
        for x in data:
            yield AsyncUtil.value_co(x)

    data = [1, 2, 3]

    result = await comp(get_gen(data))

    print(result)