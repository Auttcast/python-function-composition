from ..async_composable import AsyncComposable as f
import asyncio
import pytest

#to examine support for type hinting
def increment(value:int) -> int:
    return value + 1

inc = f(increment)
inc_pass = f(lambda x,y: (x+1, y+1))
power = f(lambda x,y: x**y)
split_num = f(lambda x: (x/2, x/2))
with_str = f(lambda x: (x, str(x)))
str_len = f(lambda x,y: len(y))
pass_thru = f(lambda x: x)

def pass_many_params(a, b, c, d):
    return (a, b, c, d)

@pytest.mark.asyncio
async def test_minimal_single_param():
    assert await inc(1) == 2

@pytest.mark.asyncio
async def test_basic_comp():
    inc2 = inc | inc
    assert await inc2(1) == 3

@pytest.mark.asyncio
async def test_long_comp():
    inc4 = inc | inc | inc | inc
    assert await inc4(1) == 5

@pytest.mark.asyncio
async def test_single_multi_param():
    (r0, r1) = await inc_pass(1, 1)
    assert r0 == 2 and r1 == 2

@pytest.mark.asyncio
async def test_multi_param():
    inc_pass4 = inc_pass | inc_pass | inc_pass | inc_pass
    (r0, r1) = await inc_pass4(1, 1)
    assert r0 == 5 and r1 == 5

@pytest.mark.asyncio
async def test_various_param():
    func = inc_pass | power | with_str | str_len
    assert await func(3, 3) == 3

@pytest.mark.asyncio
async def test_inverse_mixmatch():
    func = inc_pass | power | with_str | str_len
    assert await func(3, 3) == 3
    func2 = power | split_num | inc_pass | f(lambda x,y: (x/2) + (x/2)) | with_str | str_len
    assert await func2(4, 4) == 5

@pytest.mark.asyncio
async def test_collections():
    pass3 = pass_thru | pass_thru | pass_thru
    assert await pass3([1, 2, 3]) == [1, 2, 3]

@pytest.mark.asyncio
def range_factory(x):
    for i in range(1, x):
        yield i

@pytest.mark.asyncio
async def test_iterables():
    rf = f(range_factory)
    evens = f(lambda r: filter(lambda x: x % 2 == 0, r))
    to_list = f(lambda r: list(r))
    avg = f(lambda r: sum(r) / len(r))
    
    func = rf | evens | to_list | avg
    
    assert await func(10) == 5

def void_func():
    pass

@pytest.mark.asyncio
async def test_void():
    vf = f(void_func)
    func = vf | vf | vf
    await func()
    assert True, "does not throw"

@pytest.mark.asyncio
async def test_dynamic_wrapping():

    #test_iterables without f-wrap
    rf = f(range_factory)
    evens = lambda r: filter(lambda x: x % 2 == 0, r)
    to_list = lambda r: list(r)
    avg = lambda r: sum(r) / len(r)    
    func = rf | evens | to_list | avg
    assert await func(10) == 5

@pytest.mark.asyncio
async def test_kargs():
    
    comp = f(pass_many_params)

    assert await comp(1, 2, 3, 4) == (1, 2, 3, 4)    
    assert await comp(a=1, b=2, c=3, d=4) == (1, 2, 3, 4)
    assert await comp(1, 2, c=3, d=4) == (1, 2, 3, 4)
    assert await comp(1, 2, d=4, c=3) == (1, 2, 3, 4)

    comp3 = comp | comp | comp
    assert await comp3(1, 2, d=4, c=3) == (1, 2, 3, 4)
    
    def func4to1(a, b, c, d): return (d-c)+(b-a)
    comp4 = comp | comp | f(func4to1)
    assert await comp4(1, 2, d=4, c=3) == 2

@pytest.mark.asyncio
async def test_bug_unpacking_reusable_comp():
    myinc = f(increment)
    _ = myinc | myinc
    pre_comp = myinc

    result = await pre_comp(1)

    assert result == 2


@pytest.mark.asyncio
async def test_prepend_comp():
    main_comp = inc | inc
    pre_comp = inc | main_comp

    result = await pre_comp(1)

    assert result == 4

@pytest.mark.asyncio
async def test_coerce_sync():

    @f
    def sync_func(x):
        return x + 1
    
    result = await sync_func(1)

    assert result == 2


@pytest.mark.asyncio
async def test_partial_1_param_func():
    cat1 = f(lambda x: "0" + x)
    co = cat1 & "1"
    result = await co
    assert isinstance(result, str)
    assert result == "01"
