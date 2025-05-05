import concurrent.futures
import threading

import numba
import numba.typed
import numba.typed.listobject
from auttcomp.async_context import AsyncContext, ExecutionType
from auttcomp.parallel_context import ParallelContext
from ..extensions import Api as f
import asyncio
import pytest
import time
import concurrent
import uvloop
'''

NOTES


-------------------------------------------------------------------------------------- benchmark: 5 tests -------------------------------------------------------------------------------------
Name (time in ms)                Min                 Max                Mean            StdDev              Median               IQR            Outliers      OPS            Rounds  Iterations
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_async_io_bound          30.8668 (1.0)       31.3776 (1.00)      31.0445 (1.0)      0.0968 (1.0)       31.0317 (1.00)     0.0977 (1.0)           5;2  32.2118 (1.0)          33           1
test_parallel_io_bound       30.9094 (1.00)      31.3304 (1.0)       31.0652 (1.00)     0.1198 (1.24)      31.0217 (1.0)      0.1835 (1.88)         13;0  32.1903 (1.00)         33           1
test_async_cpu_bound         32.3815 (1.05)      39.0766 (1.25)      33.0200 (1.06)     1.1664 (12.04)     32.8583 (1.06)     0.3113 (3.19)          1;1  30.2847 (0.94)         30           1
test_parallel_cpu_bound      32.4972 (1.05)      33.1523 (1.06)      32.7964 (1.06)     0.1776 (1.83)      32.7472 (1.06)     0.2820 (2.89)          8;0  30.4911 (0.95)         29           1
test_iter                   304.3560 (9.86)     304.8425 (9.73)     304.6557 (9.81)     0.1861 (1.92)     304.7300 (9.82)     0.2142 (2.19)          2;0   3.2824 (0.10)          5           1
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''


cpu_bound_data = list(range(0, 1000))
def inc_sync(x):
    #time.sleep(0.01)
    return x+1

io_bound_data = list(range(0, 1000))
async def inc_async(x):
    #await asyncio.sleep(0.01)
    return x+1

#@pytest.mark.asyncio
def test_cpu_bound_async(benchmark):
    
    async def setup():
        asyncio.set_event_loop(asyncio.new_event_loop())

        comp = AsyncContext()(lambda f:
            f.map(inc_sync)
            | f.map(inc_sync)
            | f.map(inc_sync)
            | f.list
        )
        
        await comp(cpu_bound_data)

    benchmark(lambda: asyncio.run(setup()))


#@pytest.mark.asyncio
def test_io_bound_async(benchmark):
    
    async def setup():
        asyncio.set_event_loop(asyncio.new_event_loop())

        comp = AsyncContext()(lambda f:
            f.map(inc_async)
            | f.map(inc_async)
            | f.map(inc_async)
            | f.list
        )

        await comp(io_bound_data)

    benchmark(lambda: asyncio.run(setup()))


def test_cpu_bound_uvloop(benchmark):
    
    async def setup():

        comp = AsyncContext()(lambda f:
            f.map(inc_sync)
            | f.map(inc_sync)
            | f.map(inc_sync)
            | f.list
        )
        
        await comp(cpu_bound_data)

    benchmark(lambda: uvloop.run(setup()))


def test_io_bound_uvloop(benchmark):
    
    async def setup():

        comp = AsyncContext()(lambda f:
            f.map(inc_async)
            | f.map(inc_async)
            | f.map(inc_async)
            | f.list
        )

        await comp(io_bound_data)

    benchmark(lambda: uvloop.run(setup()))


def test_cpu_bound_processpool(benchmark):
    
    with concurrent.futures.ProcessPoolExecutor() as pool:

        async def setup():

            comp = AsyncContext(cpu_bound_executor=pool)(lambda f:
                f.map(inc_sync)
                | f.map(inc_sync)
                | f.map(inc_sync)
                | f.list
            )
            
            await comp(cpu_bound_data)

        benchmark(lambda: asyncio.run(setup()))


def test_io_bound_processpool(benchmark):
    
    with concurrent.futures.ProcessPoolExecutor() as pool:

        async def setup():

            comp = AsyncContext(cpu_bound_executor=pool)(lambda f:
                f.map(inc_async)
                | f.map(inc_async)
                | f.map(inc_async)
                | f.list
            )

            await comp(io_bound_data)

        benchmark(lambda: asyncio.run(setup()))


def test_jit_baseline(benchmark):
    
    with concurrent.futures.ProcessPoolExecutor() as pool:

        def setup():

            func = inc_sync

            comp = ParallelContext(cpu_bound_executor=pool)(lambda f:
                f.map(func)
                | f.map(func)
                | f.map(func)
                | f.list
            )

            benchmark(lambda: comp(io_bound_data))

        setup()


def test_jit_compiled(benchmark):
    
    with concurrent.futures.ProcessPoolExecutor() as pool:

        def setup():

            func = numba.njit(inc_sync)

            comp = ParallelContext(cpu_bound_executor=pool)(lambda f:
                f.map(func)
                | f.map(func)
                | f.map(func)
                | f.list
            )

            comp(io_bound_data) #seperate compilation from benchmark

            benchmark(lambda: comp(io_bound_data))

        setup()

def test_jit_temp(benchmark):
    '''
    Facts:
    -running a compiled higher order function requires the func arg also be compiled
    -list is deprecated, use number.typed.List instead
    -numba does not support async

    Speculation:
    -cpu-bound is single-threaded by default (because of the GIL, threads practically are broken)
    '''
    from numba.typed import List
    from numba import prange


    @numba.njit()
    def func1(func):
        #return List(map(func, prange(1000)))
        result = []
        
        for x in prange(10):
            result.append(func(x))
        return result
    
    @numba.njit()
    def func2(x):
        return x+1
    
    #result = func1(func2, _data)

    def testt():
        #result = pool.map(func2, range(1000))
        result = func1(func2)
        list(result)

    benchmark(testt)


def test_llvm():

    '''
    TODO
    -iterable
    -async gen
    -higher order funcs
    '''

    #from __future__ import print_function
    from ctypes import CFUNCTYPE, c_double
    import llvmlite.binding as llvm

    # All these initializations are required for code generation!
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()  # yes, even this one

    llvm_ir = """
    ; ModuleID = "examples/ir_fpadd.py"
    target triple = "unknown-unknown-unknown"
    target datalayout = ""

    define double @"fpadd"(double %".1", double %".2")
    {
    entry:
        %"res" = fadd double %".1", %".2"
        ret double %"res"
    }
    """
 
    def create_execution_engine():
        """
        Create an ExecutionEngine suitable for JIT code generation on
        the host CPU.  The engine is reusable for an arbitrary number of
        modules.
        """
        # Create a target machine representing the host
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # And an execution engine with an empty backing module
        backing_mod = llvm.parse_assembly("")
        engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
        return engine


    def compile_ir(engine, llvm_ir):
        """
        Compile the LLVM IR string with the given engine.
        The compiled module object is returned.
        """
        # Create a LLVM module object from the IR
        mod = llvm.parse_assembly(llvm_ir)
        mod.verify()
        # Now add the module and make sure it is ready for execution
        engine.add_module(mod)
        engine.finalize_object()
        engine.run_static_constructors()
        return mod


    engine = create_execution_engine()
    mod = compile_ir(engine, llvm_ir)

    # Look up the function pointer (a Python int)
    func_ptr = engine.get_function_address("fpadd")

    # Run the function via ctypes
    cfunc = CFUNCTYPE(c_double, c_double, c_double)(func_ptr)
    res = cfunc(1, 3.5)
    print(f"{type(cfunc)} fpadd(...) =", res)
