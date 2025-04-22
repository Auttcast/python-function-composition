from concurrent.futures import Executor
from enum import Enum
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Iterable, TypeVar, Union
from .async_composable import AsyncComposable
from .extensions import Api
from .composable import Composable, P, R
from .common import id_param
from asyncio import AbstractEventLoop
import asyncio
import inspect

T = TypeVar('T')
T2 = TypeVar('T2')
K = TypeVar('K')

'''
AsyncApi for IO, ParallelApi for CPU

Ubiquitous Language:
Eager Execution - The dynamic execution of task continuations composed by multiple map compositions
    between an iterable source which yields its elements as un-awaited tasks/coroutines and an eager execution boundary which awaits the tasks.
Parallel - Tasks "running" at the same time, on the same loop, not to be confused with parallel-threading.
Exit Boundary - A source enumerator which evaluates the coroutines of the previous composition(s) per the chosen behavioral ExecutionType. In context,
    map compositions create an execution chain, and any non-map is an exit boundary.

Pattern to optimize for parallelism and eager execution:
-the iterable/gen source yields non-awaited tasks or coroutines instead of values
-map compositions operate on, and yield in the same non-blocking style,
    ultimately creating a set of task continuations which will be evaluated later at an execution boundary
-eager execution is possible thru a series of consecutive maps,
in which case, every map operation is treated as a task continuation from the iterable/gen source
and will continue this pattern until a higher order function with exit_boundary is encountered
-exit_boundary (operating with ExecutionType PARALLEL_EAGER or PARALLEL_RETAIN) begins execution of each task constructed 
by the iterable/gen source (all tasks are started at the same time).
So exit_boundary requires the previously composed higher order functions to operate with constraints:
They must retain both the quantity and ordinality of the set.


Motivation for Eager Execution
Let's use map(step1) | map(step2) as an example
A traditional contemporary pattern would execute all operations on step1 before continuing to step 2.
But this is quite problematic. Recall that in async we are mostly concerned with un-blocking execution where there is IO. 
If step1 is downloading a list of items, but one item is taking significantly longer (or will eventually fail or timeout), 
we would not want this lagging item to block other tasks from continuing to step2.

reinforce a best practice: when async is used, everything should be async.
-not going to worry about async-sync type of issues here, except lambdas and sync-def funcs will coerce to CPU-bound async functions

'''

class ExecutionType(Enum):
    '''
    PARALLEL_EAGER
    tasks execute at the same time and yield on completion (order of the set does not matter)
    
    PARALLEL_RETAIN
    tasks execute at the same time and yield with consistent ordinality

    SYNC
    tasks execute and yield one at a time
    '''
    
    PARALLEL_EAGER = 1
    PARALLEL_RETAIN = 2
    SYNC = 3

class _ExtensionFactory:
    
    def __init__(self, 
                 executor:Executor=None,
                 execution_type:ExecutionType=None
                 ):
        self.__loop : AbstractEventLoop = asyncio.get_event_loop()
        self.__executor : Executor = executor
        self.__execution_type = execution_type

        self.exit_boundary = self.create_exit_boundary_strategy()

    async def __start_tasks(source_gen:AsyncGenerator[Any, T]) -> list[Coroutine[Any, Any, T]]:
        running = []
        async for d in source_gen:
            running.append(asyncio.create_task(d))
        return running
    
    def create_exit_boundary_strategy(self):
        
        if self.__execution_type == ExecutionType.PARALLEL_RETAIN:

            async def exit_boundary_parallel_retain[T](source_gen:AsyncGenerator[Any, T]) -> AsyncGenerator[Any, T]:
                for co in await _ExtensionFactory.__start_tasks(source_gen):
                    yield await co
            return exit_boundary_parallel_retain
        
        elif self.__execution_type == ExecutionType.PARALLEL_EAGER:
            
            async def exit_boundary_parallel_eager[T](source_gen:AsyncGenerator[Any, T]) -> AsyncGenerator[Any, T]:
                for co in asyncio.as_completed(await _ExtensionFactory.__start_tasks(source_gen)):
                    yield await co
            return exit_boundary_parallel_eager
        
        if self.__execution_type == ExecutionType.SYNC:

            async def exit_boundary_sync[T](source_gen:AsyncGenerator[Any, T]) -> AsyncGenerator[Any, T]:
                async for co in source_gen:
                    yield await co

            return exit_boundary_sync
        
        else:
            raise TypeError(f"self.__yield_ordinality_type: {self.__execution_type} not recognized")

    @staticmethod
    async def value_co(value):
        return value
    
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
            return self.create_cpu_bound_invocation(func)
        
    def create_map(self):

        @Composable
        def _map[T, R](func:Callable[[T], R]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, R]]:
            
            func = self.coerce_async(func)

            @AsyncComposable
            async def partial_map(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[R]]:
                async for co in source_gen:
                    yield _ExtensionFactory.__co_map_exec(func, co)
                    
            return partial_map
        return _map

    def create_filter(self):

        @Composable
        def _filter[T](func:Callable[[T], bool]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, T]]:

            func = self.coerce_async(func)

            @AsyncComposable
            async def partial_filter(source_gen: AsyncGenerator[Any, Awaitable[T]]) -> AsyncGenerator[Any, Awaitable[T]]:
                async for value in self.exit_boundary(source_gen):
                    if await func(value):
                        yield _ExtensionFactory.value_co(value)
                    
            return partial_filter
        return _filter

    def create_foreach(self):
            
        @Composable
        def _foreach(func: Callable[[T], R]) -> Callable[[AsyncGenerator[Any, Awaitable[T]]], None]:
            '''exec the func for each element in the iterable'''

            func = self.coerce_async(func)

            @AsyncComposable
            async def partial_foreach(data: AsyncGenerator[Any, Awaitable[T]]) -> None:
                async for x in self.exit_boundary(data):
                    await func(x)

            return partial_foreach
        return _foreach

    def create_list(self):
        
        @AsyncComposable
        async def _list[T](source_gen:AsyncGenerator[Any, Awaitable[T]]) -> list[T]:
            result_list = []        
            async for result in self.exit_boundary(source_gen):
                result_list.append(result)
            return result_list
        
        return _list


    def create_flatmap(self):
            
        @Composable
        def flatmap(func: Callable[[T], R] = id_param) -> Callable[[AsyncGenerator[Any, Iterable[T]]], AsyncGenerator[Any, R]]:
            
            func = self.coerce_async(func)

            @AsyncComposable
            async def partial_flatmap(source_gen: AsyncGenerator[Any, Iterable[T]]) -> AsyncGenerator[Any, R]:
                async for x1 in self.exit_boundary(source_gen):
                    for x2 in await func(x1):
                        yield _ExtensionFactory.value_co(x2)

            return partial_flatmap
        
        return flatmap

class AsyncApi(AsyncComposable[P, R]):

    def __init__(self, factory:_ExtensionFactory):
        self.map = factory.create_map()
        self.flatmap = factory.create_flatmap()
        self.filter = factory.create_filter()
        self.list = factory.create_list()
        
class AsyncContext:

    '''
    cpu_bound_executor
    The thread or process pool used to execute syncronous functions

    execution_type
    How generative sources are processed at an execution boundary
    Default (None) uses ThreadPoolExecutor implemented by loop.run_in_executor
    '''

    def __init__(self, 
                 cpu_bound_executor:Executor=None, 
                 execution_type:ExecutionType=ExecutionType.PARALLEL_RETAIN
                 ):
        
        self.factory = _ExtensionFactory(cpu_bound_executor, execution_type)

    @staticmethod
    @AsyncComposable
    async def source_adapter[T](data:Union[AsyncGenerator[Any, T] | Iterable[T]]) -> AsyncGenerator[Any, T]:
        
        if isinstance(data, Iterable):
            for value in data:
                yield _ExtensionFactory.value_co(value)
        elif isinstance(data, AsyncGenerator):
            async for value in data:
                if isinstance(value, Coroutine):
                    yield value
                else:
                    yield _ExtensionFactory.value_co(value)
        else:
            raise TypeError(f"data type {type(data)} not supported")

    @staticmethod
    def exit_boundary(factory):

        @AsyncComposable
        async def partial_exit_boundary(data):
            if isinstance(data, AsyncGenerator):
                return factory.exit_boundary(data)
            
            return data
        
        return partial_exit_boundary

    def __call__(self, composition_factory:Callable[[AsyncApi], AsyncComposable]) -> AsyncComposable:

        return (
            AsyncContext.source_adapter 
            | composition_factory(AsyncApi(self.factory)) 
            | AsyncContext.exit_boundary(self.factory)
            )
