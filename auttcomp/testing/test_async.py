from typing import Any, AsyncGenerator, Callable, Iterable
from auttcomp.async_composable import AsyncComposable
from ..extensions import Api as f
import asyncio
import pytest

class AsyncApi:

    def map[T, R](self, func:Callable[[T], R]) -> Callable[[AsyncGenerator[Any, T]], AsyncGenerator[Any, R]]:
        
        @AsyncComposable
        async def partial_map(data: AsyncGenerator[Any, T]) -> AsyncGenerator[Any, R]:
            '''
            fanout?
            '''
            
            running = []
            async for d in data:
                running.append(func(d))
                
            for complete in asyncio.as_completed(running):
                yield await complete

        return partial_map

    @staticmethod
    @AsyncComposable
    async def list[T](data:AsyncGenerator[Any, T]) -> list[T]:
        result = []
        async for d in data:
            result.append(d)
        return result

class AsyncContext:

    '''
    reinforce a best practice: when async is used, everything should be async.
    -not going to worry about async-sync type of issues

    context will lift Iterable to AsyncGenerator (if not already)
    '''

    @staticmethod
    @AsyncComposable
    async def iterable_to_async_gen[T](data:Iterable[T]) -> AsyncGenerator[Any, T]:
        #todo match iter, gen, _ (scalar)
        for d in data:
            yield d

    def __call__(self, composition_factory:Callable[[AsyncApi], AsyncComposable]) -> AsyncComposable:
        return AsyncContext.iterable_to_async_gen | composition_factory(AsyncApi())

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

    '''
    prereq: test_comp_w_id_invoke
    cancellation
    iterable/ag - AsyncContext adapter

    caveat
    async composition
    async gen and coroutines are not very composable because of await

    option1:
    custom awaitable async gen

    '''

    async def get_gen():
        for x in range(0, 3):
            yield x

    async def inc_async(x):
        print('start')
        await asyncio.sleep(1)
        return x + 1
    
    api = AsyncApi()


    comp = (
        api.map(inc_async) 
        | api.map(inc_async) 
        | api.list
        )
    result = await comp(get_gen())
    print(result)

    # data = [2, 1, 3]

    # async_comp = AsyncContext()(lambda f: (
    #     f.map(inc_async)
    #     | f.list
    # ))
        
    # result_list = async_comp(data)
    # print(result_list)
    # gen = await result_list
    # print(gen)
    # async for x in gen:
    #     print(x)
    

@pytest.mark.asyncio
async def test_async_comps():

    '''
    () -> ag | (ag) -> int

    just check if response is awaitable

    '''

    async def test2():
        return 123
    
    async def test1():
        return await test2()

    print(await test1())

    @AsyncComposable
    async def get_gen() -> AsyncGenerator[Any, int]:
        for x in range(0, 3):
            yield x

    @AsyncComposable
    async def get_co(ag:AsyncGenerator[Any, int]) -> int:
        await asyncio.sleep(1)
        count = 0
        async for x in ag:
            count += 1
        return count
    
    comp = get_gen | get_co

    x = await comp()

    print(x)

