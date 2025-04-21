from concurrent.futures import Executor
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Iterable, TypeVar, Union
from auttcomp.async_composable import AsyncComposable
from .composable import Composable, P, R
from .common import id_param
from asyncio import AbstractEventLoop
import asyncio
import inspect

T = TypeVar('T')
T2 = TypeVar('T2')
K = TypeVar('K')

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


class _ExtensionFactory:
    '''
    instance or factory comp
    coerce_async will become an instance method and access executor,loop
    '''
    def __init__(self, executor:Executor=None):
        self.__loop : AbstractEventLoop = asyncio.get_event_loop()
        self.__executor : Executor = executor

    @staticmethod
    async def __co_map_exec(co_func, co):
        return await co_func(await co)

    def create_cpu_bound_invocation(self, func):
        async def partial_invoke_cpu_bound(*args):
            return await self.__loop.run_in_executor(self.__executor, func, *args)
        return partial_invoke_cpu_bound

    def coerce_async(self, func):
        if inspect.iscoroutinefunction(func):
            return func
        else:
            #return AsyncUtil.as_async(func)
            return self.create_cpu_bound_invocation(func)
        
    def create_map(self):

        @Composable
        def map[T, R](func:Callable[[T], R]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, R]]:
            
            func = self.coerce_async(func)

            @AsyncComposable
            async def partial_map(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[R]]:
                async for co in source_gen:
                    yield _ExtensionFactory.__co_map_exec(func, co)
                    
            return partial_map
        return map


class AsyncApi(Composable[P, R]):

    def __init__(self, executor:Executor=None):
        factory = _ExtensionFactory(executor)

        self.map = factory.create_map()
        

    '''
    AsyncApi for IO, ParallelApi for CPU

    Ubiquitous Language:
    Eager Execution - The dynamic execution of task continuations composed by multiple qualifying higher order functions (namely map and flatmap)
        between an iterable source which yields its elements as un-awaited tasks/coroutines and an eager execution boundary which awaits the tasks.
    Parallel - Tasks "running" at the same time, on the same loop, not to be confused with parallel-threading.
    Eager Boundary - A source enumerator which evaluates the coroutines of the previous compositions.
    
    Pattern to optimize for parallelism and eager execution:
    -the iterable/gen source yields non-awaited tasks or coroutines instead of values
    -compositions (map,flatmap) operate on, and yield in the same non-blocking style,
      ultimately creating a set of task continuations which will be evaluated later at an eager boundary
    -eager execution is possible thru a series of consecutive maps,
    in which case, every map operation is treated as a task continuation from the iterable/gen source
    and will continue this pattern until a higher order function with eager_boundary is encountered
    -eager_boundary begins execution of each task constructed by the iterable/gen source (all tasks are started at the same time).
    So eager_boundary requires the composed higher order functions to operate with constraints:
    They must retain both the quantity and ordinality of the set.

    
    Motivation for Eager Execution
    Let's use map(step1) | map(step2) as an example
    A traditional contemporary pattern would execute all operations on step1 before continuing to step 2.
    But this is quite problematic. Recall that in async we are mostly concerned with un-blocking execution where there is IO. 
    If step1 is downloading a list of items, but one item is taking significantly longer (or will eventually fail or timeout), 
    we would not want this lagging item to block other tasks from continuing to step2.

    
    functions qualifying for eager continuation/execution:
        map
        flatmap

    reinforce a best practice: when async is used, everything should be async.
    -not going to worry about async-sync type of issues here, except lambdas will coerce to async

    Reminder:
    -Bridging async and parallel CPU
    -handling cancellations and failed tasks
    
    Brainstorming
    sometimes, long-running CPU can be considered IO. The design so far has been distinctly seperate AsyncApi for IO and ParallelApi for CPU

    speculation
    -from coercion to Seperation of Concern
    -bring AsyncApi method back to non-static, support composable instance-methods (accessing executor and loop for customization)
    -AsyncContext(executor?) - loop as asyncio.get_running_loop() for now
    -coerce_async: [speculative convention] async func is IO bound, sync func is CPU bound (made async with loop.run_in_executor)
    '''

    @staticmethod
    async def __co_map_exec(co_func, co):
        return await co_func(await co)

    @staticmethod
    @AsyncComposable
    def filter[T](func:Callable[[T], bool]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, T]]:

        func = AsyncUtil.coerce_async(func)

        @AsyncComposable
        async def partial_filter(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[T]]:
            async for value in AsyncUtil.eager_boundary(source_gen):
                if await func(value):
                    yield AsyncUtil.value_co(value)
                
        return partial_filter

    @staticmethod
    @AsyncComposable
    async def list[T](source_gen:AsyncGenerator[Any, Awaitable[T]]) -> list[T]:
        results = []        
        async for d in AsyncUtil.eager_boundary(source_gen):
            results.append(d)
        return results

    @staticmethod
    @AsyncComposable
    def foreach(func: Callable[[T], R]) -> Callable[[AsyncGenerator[Any, Awaitable[T]]], None]:
        '''exec the func for each element in the iterable'''

        func = AsyncUtil.coerce_async(func)

        @AsyncComposable
        async def partial_foreach(data: AsyncGenerator[Any, Awaitable[T]]) -> None:
            async for x in AsyncUtil.eager_boundary(data):
                await func(x)

        return partial_foreach

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
