bringing inline composition to python (like from your favorite languages F#, powershell, kql, haskell, etc)

## Guide

### Composition with |

g(f(x)) == (f | g)(x)

To achieve inline composition, any callables must be wrapped with the Composable object

```python
from auttcomp.extensions import Api as f

square = f(lambda x: x ** 2)
add3 = f(lambda x: x + 3)

comp = square | add3
assert comp(3) == 12
```

### Automatic wrapping

If the composition chain starts with a Compsable, the rest of the chain is automatically wrapped!

```python
from auttcomp.extensions import Api as f

square = f(lambda x: x ** 2)
add3 = lambda x: x + 3

comp = square | add3 | (lambda x: x + 10)
assert comp(3) == 22
```

### Partial Application with &

Consider python's map function - map(func, data)

In this example, & is used to partially apply the square func to map

```python
from auttcomp.extensions import Api as f

square = lambda x: x ** 2
cmap = f(map)
pmap = cmap & square

assert list(pmap([1, 2, 3])) == [1, 4, 9]
```

### Identity functions and invocation with >

When Composable receives a non-callable type, it constructs an identify function for that data

```python
from auttcomp.extensions import Api as f
from auttcomp.testing.testBase import getHuggingFaceSample

data = getHuggingFaceSample()

f(data)
```

The data in this sample is a search result from the Hugging Face api. 

We'll explore the data with a query soon, but first we'd like to know about it's structure. So we'll invoke the f.shape function

Because ">" is used, the identify function is invoked. This pipes the data into the f.shape function.

The f.shape function will tell us about the format of this data structure!

```python
f(data) > f.shape
```

Which returns the following:

```python
{ 'activeFilters': { 'dataset': [],
                     'language': [],
                     'library': [],
                     'license': [],
                     'other': [],
                     'pipeline_tag': []},
  'models': [ { 'author': 'str',
                'authorData': { '_id': 'str',
                                'avatarUrl': 'str',
                                'followerCount': 'int',
                                'fullname': 'str',
                                'isEnterprise': 'bool',
                                'isHf': 'bool',
                                'isMod': 'bool',
                                'isPro': 'bool',
                                'name': 'str',
                                'type': 'str'},
                'downloads': 'int',
                'gated': 'bool|str',
                'id': 'str',
                'inference': 'str',
                'isLikedByUser': 'bool',
                'lastModified': 'str',
                'likes': 'int',
                'pipeline_tag': 'str',
                'private': 'bool',
                'repoType': 'str',
                'widgetOutputUrls': ['str']}],
  'numItemsPerPage': 'int',
  'numTotalItems': 'int',
  'pageIndex': 'int'}
```

### Extensions API

TODO

## Testing
pytest 7.4.3

## Misc
Python 3.12.8

No dependencies outside of core python
