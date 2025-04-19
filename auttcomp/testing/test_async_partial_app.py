from typing import Callable

from auttcomp.async_context import AsyncContext
from ..async_composable import AsyncComposable as f
import pytest

@pytest.mark.asyncio
async def test_partial_1_param_func():
    cat1 = f(lambda x: "0" + x)
    result = await (cat1 & "1")
    assert isinstance(result, str)
    assert result == "01"

@pytest.mark.asyncio
async def test_partial_2_param_func():
    cat2_l:Callable[[str, str], str] = lambda a, b: "0" + a + b
    cat2 = f(cat2_l)
    get1 = cat2 & "1"
    assert await get1("2") == "012"

    result1 = await (get1 & "2")
    assert result1 == "012"

    result2 = await (cat2 & "1" & "2")
    assert result2 == "012"

@pytest.mark.asyncio
async def test_partial_multi_param_func():
    cat3 = f(lambda a, b, c: "0" + a + b + c)
    get1 = cat3 & "1"
    assert await get1("2", "3") == "0123"

    get2 = cat3 & "1" & "2"
    assert await get2("3") == "0123"

    get3 = await (cat3 & "1" & "2" & "3")
    assert get3 == "0123"

@pytest.mark.asyncio
async def test_partial_multi_param_func2():

    #this test demonstrates that when functions are already curried, they are not within the composable's domain

    cat3 = f(lambda a: lambda b: lambda c: "0" + a + b + c)
    get1 = await cat3("1")
    assert get1("2")("3") == "0123"

    #NOT composable!
    assert not isinstance(get1, f)

    get2 = (await cat3("1"))("2")
    assert get2("3") == "0123"

    get3 = (await cat3("1"))("2")("3")
    assert get3 == "0123"

@pytest.mark.asyncio
async def test_partial_on_no_param_throws():
    zero_param_func = f(lambda: "hi")

    try:
        zero_param_func & "1"
        assert False, "expected to throw!"
    except TypeError:
        pass
    except Exception:
        assert False, "wrong exception type"

@pytest.mark.asyncio
async def test_partial_on_curried_composable_func():
    
    curried_add = f(lambda x: f(lambda y: x + y))
    
    curried_add_1 = await (curried_add & 1)
    
    assert await curried_add_1(1) == 2
    
@pytest.mark.asyncio
async def test_partial_on_curried_composable_func_with_composition():
    
    data = [1, 2, 3]

    plus2comp = AsyncContext()(lambda f: (
        f.map & (lambda x: x + 1) 
        | f.map & (lambda x: x + 1) 
        | f.list
    ))

    expected = [3, 4, 5]

    actual = await plus2comp(data)

    assert actual == expected

    
@pytest.mark.asyncio
async def test_partial_callable_class():
    
    data = [1, 2, 3]
    plus1 = f(map) & (lambda x: x + 1)
    expected = [2, 3, 4]

    actual = list(await plus1(data))

    assert actual == expected

@pytest.mark.asyncio
async def test_partial_callable_class2():
    
    data = [1, 2, 3]
    plus2 = f(map) & (lambda x: x + 1) | f(map) & (lambda x: x + 1)
    expected = [3, 4, 5]

    actual = list(await plus2(data))

    assert actual == expected
