from ..async_composable import AsyncComposable
from ..extensions import Api as f
import asyncio
import pytest

@pytest.mark.asyncio
async def test_comp_w_id_invoke():

    @AsyncComposable
    async def test_func(x:int) -> int:
        await asyncio.sleep(0)
        return x+1

    comp = test_func | test_func | test_func

    r = await (f.id(1) > comp)

    assert r == 4
