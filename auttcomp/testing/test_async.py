from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Iterable, Union
from auttcomp.async_composable import AsyncComposable
from ..extensions import Api as f
import asyncio
import pytest

class AsyncApi:

    '''
    Pattern to optimize for parallelism and eager execution:
    aggregators and terminators(like list), should exec all tasks from the async gen first,
    
    reinforce a best practice: when async is used, everything should be async.
    -not going to worry about async-sync type of issues here, except for lambdas

    todo:
    -bug fix missing f.list
    -consider custom AsyncApi.iter which would support the execution pattern, but adapt to iterable instead
    -async lambda workaround


    review
    the eager parallel model seems powerful, however it is limited in that one cannot easily determine if yields from async_gen have been cancelled.
    this means that applying an intermediate adapter among the higher order functions is not practical, for implementing filter per task cancellation

    while I do like this execution model quite a lot, perhaps it would be best to form it into a more limited contextual fluent api
    one that forces ordering, since .filter cannot run after .map here.

    maybe it is possible with asyncio.current_task() within the exec functions ? but I don't like the idea of, for example,
    having a huge list filtered to only a massive list, and the further continuations executing, still, a huge list of cancellations. 
    contextual fluent sounds much more practical

    tentative
    AsyncContext will later be reworked for general purpose async
    the current code will be labeled something like AsyncEagerContext

    AsyncEagerContext outline
    The operations for each higher order function and element of data are executed as quickly as possible.
    This requires all higher order functions to yield a defered execution and a terminating function (like .list or some aggregate) 
    to run the stack of compositions.
    Consequently, filter can only be implemented as a task cancellation and further maps after filter are not practical
    '''

    @staticmethod
    async def __co_map_exec(co_func, co):
        return await co_func(await co)

    def map[T, R](self, func:Callable[[T], R]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, R]]:
        
        @AsyncComposable
        async def partial_map(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[R]]:
            async for co in source_gen:
                yield AsyncApi.__co_map_exec(func, co)
                
        return partial_map

    @staticmethod
    async def __co_filter_exec(filter_func_co, source_co):
        value = await source_co
        if await filter_func_co(value):
            return value
        asyncio.current_task().cancel()
    

    def filter[T](self, func:Callable[[T], bool]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, T]]:
        '''
        filter implemented with eager execution
        if an element is filtered, the task is canceled
        '''
        @AsyncComposable
        async def partial_map(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[T]]:
            async for co in source_gen:
                yield AsyncApi.__co_filter_exec(func, co)
                
        return partial_map

    @staticmethod
    @AsyncComposable
    async def list[T](source_gen:AsyncGenerator[Any, Awaitable[T]]) -> list[T]:
        
        running = []
        async for d in source_gen:
            t = asyncio.create_task(d)
            running.append(t)

        results = []
        for c in running:
            if not c.cancelled():
                r = await c
                results.append(r)

        return results

class AsyncContext:

    @staticmethod
    @AsyncComposable
    async def source_adapter[T](data:Union[AsyncGenerator[Any, T] | Iterable[T]]) -> AsyncGenerator[Any, T]:
        
        if isinstance(data, Iterable):
            for x in data:
                yield asyncio.sleep(0, x)
        elif isinstance(data, AsyncGenerator):
            async for x in data:
                if isinstance(x, Coroutine):
                    yield x
                else:
                    yield asyncio.sleep(0, x)
        else:
            raise TypeError(f"data type {type(data)} not supported")

    def __call__(self, composition_factory:Callable[[AsyncApi], AsyncComposable]) -> AsyncComposable:
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
async def test_map_ext():

    async def inc_async(x):
        await asyncio.sleep(x)
        return x + 1
    
    async def test_filter_async(x):
        return x != 3

    data = [2, 1, 2]

    async_comp = AsyncContext()(lambda f: (
        f.map(inc_async)
        | f.map(inc_async)
        | f.filter(test_filter_async)
        | f.list
        | f.list
    ))
        
    result = await async_comp(data)
    print(result)
