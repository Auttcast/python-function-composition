import inspect
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Iterable, Union
from auttcomp.async_composable import AsyncComposable
import asyncio

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
    -not going to worry about async-sync type of issues here, except lambdas will coerce to async

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

    @staticmethod
    @AsyncComposable
    async def exit_boundary(data):
        if isinstance(data, AsyncGenerator):
            return AsyncUtil.eager_boundary(data)
        return data

    def __call__(self, composition_factory:Callable[[AsyncApi], AsyncComposable]) -> AsyncComposable:
        return AsyncContext.source_adapter | composition_factory(AsyncApi()) | AsyncContext.exit_boundary
