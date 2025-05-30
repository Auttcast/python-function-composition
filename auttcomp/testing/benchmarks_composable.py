from ..composable import Composable as f

'''
test_1*
these tests demonstrate the performance impact of invoking compositions compared to native invocations

pytest auttcomp/testing/benchmarks.py
pytest auttcomp/testing/benchmarks.py --benchmark-histogram

'''

def increment(x):
    return x+1

def get_1():
    return 1

def native_1():
    increment(get_1())

def test_1_native_1(benchmark):
    benchmark(native_1)

def native_2():
    increment(increment(get_1()))

def test_1_native_2(benchmark):
    benchmark(native_2)

def native_3():
    increment(increment(increment(get_1())))

def test_1_native_3(benchmark):
    benchmark(native_3)

def native_4():
    increment(increment(increment(increment(get_1()))))

def test_1_native_4(benchmark):
    benchmark(native_4)

def test_1_composition_1(benchmark):
    composition = f(get_1) | f(increment)
    benchmark(composition)

def test_1_composition_2(benchmark):
    composition = f(get_1) | f(increment) | f(increment)
    benchmark(composition)

def test_1_composition_3(benchmark):
    composition = f(get_1) | f(increment) | f(increment) | f(increment)
    benchmark(composition)

def test_1_composition_4(benchmark):
    composition = f(get_1) | f(increment) | f(increment) | f(increment) | f(increment)
    benchmark(composition)
