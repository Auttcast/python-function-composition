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

def test_1_native_1(benchmark):
    benchmark(lambda: increment(get_1()))

def test_1_native_2(benchmark):
    benchmark(lambda: increment(increment(get_1())))

def test_1_native_3(benchmark):
    benchmark(lambda: increment(increment(increment(get_1()))))

def test_1_native_4(benchmark):
    benchmark(lambda: increment(increment(increment(increment(get_1())))))

def test_1_composition_1(benchmark):
    composition = f(get_1) | f(increment)
    benchmark(lambda: composition())

def test_1_composition_2(benchmark):
    composition = f(get_1) | f(increment) | f(increment)
    benchmark(lambda: composition())

def test_1_composition_3(benchmark):
    composition = f(get_1) | f(increment) | f(increment) | f(increment)
    benchmark(lambda: composition())

def test_1_composition_4(benchmark):
    composition = f(get_1) | f(increment) | f(increment) | f(increment) | f(increment)
    benchmark(lambda: composition())
