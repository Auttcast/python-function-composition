light weight wrapper for inline-pipe functional composition in python

## Usage

```python
import composable

f = composable.Composable

incPass = f(lambda x,y: (x+1, y+1))
power = f(lambda x,y: x**y)
withStr = f(lambda x: (x, str(x)))
strLen = f(lambda x,y: len(y))

def test_various_param():
  func = incPass | power | withStr | strLen
  assert func(3, 3) == 3
```

## Design Notes
Minimal design in a single class - Composable

Currently it only wraps individual lambdas/function by explicitely invoking Composable, as it is a callable class

The class overrides the pipe operator so that it may interact with other Composables to form a composition

So Composable(func) (or just f(func)) returns a wrapped function

When inline-composition is invoked thru the pipe operator, an addition Composable object is created which chains the two functions together

Effectively, h(k(g(f(x)))) can now be represented as (f | g | k | h)(x)

## Considering TODOs
* automatic wrapping for classes, attributes, etc
* exception handling, type hinting

## Testing
pytest 7.4.3

## Misc
Python 3.12.8

No dependencies outside of core python
