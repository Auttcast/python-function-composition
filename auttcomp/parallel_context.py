from concurrent.futures import Executor
from typing import Any, AsyncGenerator, Callable
from auttcomp.async_composable import AsyncComposable
from auttcomp.composable import Composable
from .async_context import AsyncApi, AsyncContext
from .common import id_param
from .async_context import ExecutionType
import asyncio

class ParallelContext:
    
    def __init__(self, 
                 cpu_bound_executor:Executor=None, 
                 execution_type:ExecutionType=ExecutionType.PARALLEL_RETAIN
                 ):
        self.cpu_bound_executor = cpu_bound_executor
        self.execution_type = execution_type

    @staticmethod
    @AsyncComposable
    async def exit_boundary[T](data) -> list[T]:
        if isinstance(data, AsyncGenerator):
            result = []
            async for x in data:
                result.append(x)
            return result
        else:
            return data

    async def __internal_call_async(self, composition_factory, *args):
        context = AsyncContext(self.cpu_bound_executor, self.execution_type)
        comp = context(composition_factory) | ParallelContext.exit_boundary
        return await comp(*args)

    def __internal_call(self, composition_factory):

        @Composable
        def partial_internal_call(*args):
            return asyncio.run(self.__internal_call_async(composition_factory, *args))
        
        return partial_internal_call

    def __call__(self, composition_factory:Callable[[AsyncApi], AsyncComposable]) -> Composable:
        return self.__internal_call(composition_factory)
