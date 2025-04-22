```
pip install auttcomp
```

## Guide

### Composition with |

g(f(x)) == (f | g)(x)

To achieve inline composition, functions must be wrapped with the Composable object (f)

```python
from auttcomp.composable import Composable as f

square = f(lambda x: x ** 2)
add3 = f(lambda x: x + 3)

comp = square | add3
assert comp(3) == 12
```

### Automatic wrapping

If the composition chain starts with a Composable, the rest of the chain is automatically wrapped

```python
from auttcomp.composable import Composable as f

square = f(lambda x: x ** 2)
add3 = lambda x: x + 3

comp = square | add3 | (lambda x: x + 10)
assert comp(3) == 22
```

### Partial Application with &

Consider python's map function - map(func, data)

In this example, & is used to partially apply the square func to map

```python
from auttcomp.composable import Composable as f

square = lambda x: x ** 2
pmap = f(map) & square

assert list(pmap([1, 2, 3])) == [1, 4, 9]
```

### Extensions Api primer: Identity function and invocation with >

The proceeding examples will import the extensions api as f. The api itself is composable, but also contains many extension methods which are commonly used on iterable data structures.

f.id is used to create a composable identity function. You will soon see that this will be the root of our composition pipeline. Conceptually we can think of this as SQL's "select * from table"

```python
import requests
import json
from types import SimpleNamespace
from typing import Iterable
from pprint import pprint
from auttcomp.extensions import Api as f

def get_data(url):
  response = requests.get(url)
  response_str = response.content.decode()
  response_obj = json.loads(response_str, object_hook=lambda d: SimpleNamespace(**d))
  return response_obj


data = get_data("https://api.github.com/users/auttcast/repos")

id_func = f.id(data)
just_data_models_again = id_func()
```

We'll explore the data with a query soon, but first we'd like to know about it's structure. It is difficult to understand the structure of the model just by looking at the raw data, so we'll use the f.shape function to help us understand it.

The f.shape function accepts any data as input, and prints a summary to the console.

While it is possible to call **f.shape(data)**, instead we'll start using a more query-friendly syntax like so:

```python
f.id(data) > f.shape
```

There are too many fields to show, but here is a glance of the result:

```python
[ { 'allow_forking': 'bool',
    'archive_url': 'str',
    'archived': 'bool',
    'assignees_url': 'str',
    'blobs_url': 'str',
    'branches_url': 'str',
    'clone_url': 'str',
    'collaborators_url': 'str',
    'comments_url': 'str',
    'commits_url': 'str',
    'compare_url': 'str',
    'contents_url': 'str',
    'contributors_url': 'str',
    'created_at': 'str',

....
```

### Extensions Api

Python already has many common higher order functions (map, filter, reduce, etc). Those functions, and others can be implemented as follows.

```python
#lists the name of each repo
f.id(data) > f(map) & (lambda x: x.name) | list
```

However, for convenience, many common functions have been curried and attached to f. So the same query could also be described as...

```python
f.id(data) > f.map(lambda x: x.name) | list
```

or even...

```python
get_name = lambda x: x.name
comp = f.map & get_name | list
f.id(data) > comp
```

### Example query

Let's create a query that will show us details about the repos.

I'll be using f.shape or pprint to get a good look at the data along the way.

First, the result is quite large, so I'm going to trim it down to just the information I want to see.

```python
f.id(data) > f.map(lambda x: (x.name, x.language, x.url)) | list | pprint
```
```python
[('AzureSqlPoolConnectionStats',
  'PowerShell',
  'https://api.github.com/repos/Auttcast/AzureSqlPoolConnectionStats'),
 ('CombinationSolver',
  'C#',
  'https://api.github.com/repos/Auttcast/CombinationSolver'),
  ....
```

I noticed one of the repos does not have a language specified, so I am going to apply a filter to ensure there is a value.

I'm also going to start using this alternative syntax, as it will make things easier to read...

```python
f.id(data) > (
  f.filter(lambda x: x.language is not None)
  | f.map(lambda x: (x.name, x.language, x.url)) 
  | list 
  | pprint
)
```

Next, I'll work in a download for the /branches request.

```python
def get_branches(base_url):
  branch_url = f"{base_url}/branches"
  result = get_data(branch_url)
  return len(result)

f.id(data) > (
  f.filter(lambda x: x.language is not None)
  | f.map(lambda x: (x.name, x.language, get_branches(x.url))) 
  | list 
  | pprint
)
```
```python
[('AzureSqlPoolConnectionStats', 'PowerShell', 1),
 ('CombinationSolver', 'C#', 1),
 ('pynes', 'Python', 1),
 ('python-function-composition', 'Python', 4),
 ('shape_eval', 'Python', 1),
 ('space-engineers-scripts', 'C#', 1),
 ('TempestWeatherDataDownload', 'PowerShell', 1)]
```

There are many other useful functions on the extentions api

```python
f.id(data) > (
  f.filter(lambda x: x.language is not None)
  | f.map(lambda x: (x.name, x.language, get_branches(x.url))) 
  | f.group(lambda x: x[1]) # group by language
  | f.sort_by_desc(lambda x: len(x[1]))
  | f.take(1)
  | list 
)
```

```python
[KeyValuePair(key='Python', value=[('pynes', 'Python', 1), ('python-function-composition', 'Python', 4), ('shape_eval', 'Python', 1)])]

```

## Async and Parallel

Version 3.0.0 added AsyncContext and ParallelContext

Currently, only a few extention methods are supported
* map
* flatmap
* filter
* list

Implementation Details:
* Both AsyncContext and ParallelContext are designed parallel-first. In fact, ParallelContext is basically just a wrapper around AsyncContext (using asyncio.run internally), so they offer practically the same functionality.
* Consecutive map compositions uniquely benefit from eager execution. For example, consider f.map(step1) | f.map(step2) ... Any operation that has completed step1 will immediately continue to step2 without waiting for the rest of the set to complete.
* IO and CPU bound convention. Higher-order functions accept both sync and async function arguments. If the function is **async**, then it is IO-bound by convention, in which case it will simply be awaited. If the function is **sync**, then it is CPU-bound, in which case it will be awaited as a dispatch to the default thread pool used by the asyncio loop.run_in_executor
* Both AsyncContext and ParallelContext accept configurations to customize execution.

Here's how ParallelContext can make a slight improvement to the previous example code

```python
from auttcomp.parallel_context import ParallelContext

parallel_result = f.id(data) > ParallelContext()(lambda f:
  f.filter(lambda x: x.language is not None)
  | f.map(lambda x: (x.name, x.language, get_branches(x.url)))
  | f.list
) 

f.id(parallel_result) > (
  f.group(lambda x: x[1]) # group by language
  | f.sort_by_desc(lambda x: len(x[1]))
  | f.take(1)
  | list 
)
```

*Note that **f** is being overriden within the ParllelContext*

So this is an improvement. The code executes much faster with few changes.

While ParallelContext is a good choice for the syncronous environment. Async code offers the best usage of system resources. Especially when there is an IO-bound operation like a web request.

Here's the same example updated for async:

```python
from auttcomp.async_context import AsyncContext
import asyncio
import aiohttp

async def get_data_async(url):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      text_result = await response.text()
      response_obj = json.loads(text_result, object_hook=lambda d: SimpleNamespace(**d))
      return response_obj

async def get_branches_async(base_url):
  branch_url = f"{base_url}/branches"
  result = await get_data_async(branch_url)
  return len(result)

async def with_branches_async(x):
  branch_detail = await get_branches_async(x.url)
  return (x.name, x.language, branch_detail)

async def main():
  async_result = await (f.id(data) > AsyncContext()(lambda f:
    f.filter(lambda x: x.language is not None)
    | f.map(with_branches_async)
    | f.list
  ))
  iter_result = f.id(async_result) > (
    f.group(lambda x: x[1]) # group by language
    | f.sort_by_desc(lambda x: len(x[1]))
    | f.take(1)
    | list 
  )
  pprint(iter_result)

asyncio.run(main())

```

A lot has changed with the sample. The map func within AsyncContext (with_branches_async), get_data, and get_branches were replaced with async implementations. But the effect is that rather than having a thread blocking and waiting on the http response, the code is now able to await the response, yielding execution time to other tasks, without requiring many additional threads, yet providing the illusion that the execution is still parallel.

## Testing
pytest 7.4.3

## Misc
developed on Python 3.12.8
