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

(note this does not apply to & (partial application) nor > (identity invocation)

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

f(data.models)
```

The data in this sample is a search result from the Hugging Face api. 

We'll explore the data with a query soon, but first we'd like to know about it's structure. So we'll invoke the f.shape function

Because ">" is used, the identify function is invoked. This pipes the data into the f.shape function.

The f.shape function will tell us about the format of this data structure!

```python
f(data.models) > f.shape
```

Which returns the following:

```python
[ { 'author': 'str',
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
    'widgetOutputUrls': ['str']}]
```

### Extensions Api

Python already has many common higher order functions (map, filter, reduce, etc). Those functions, and others can be implemented as follows.

```python
#list the author of each model
f(data.models) > f(map) & (lambda x: x.authorData) | f(map) & (lambda x: x.name) | list
```

However, for convenicne, many common functions have been curried and attached to f. So the same query could also be described as...

```python
f(data.models) > f.map(lambda x: x.authorData) | f.map(lambda x: x.name) | list
```

or even...

```python
getAuthorData = lambda x: x.authorData
getName = lambda x: x.name
comp = f.map & getAuthorData | f.map & getName | list
f(data.models) > comp
```

### Example query

Let's create a list which shows the authors with the most downloads.

f.shape will be used to show the result of the query at each stage.

First, group by author

```python
f(data.models) > f.group(lambda x: x.author) | list | f.shape
```
```python
[ { 'key': 'str',
    'value': [ { 'author': 'str',
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
                 'widgetOutputUrls': ['str']}]}]
```

Map to (key, sumDownloads)

```python
f(data.models) > (
  f.group(lambda x: x.author)
  | f.map(lambda g: (
    g.key,
    f(g.value) > f.map(lambda x: x.downloads) | sum )
  ) | list | f.shape
)
```
```python
[('str', 'int')]
```

Sort by descending downloads and take the top 5 results

```python
f(data.models) > (
  f.group(lambda x: x.author)
  | f.map(lambda g: (
    g.key,
    f(g.value) > f.map(lambda x: x.downloads) | sum )
  )
  | f.sortByDescending(lambda x: x[1])
  | f.take(5))
```
```python
[('black-forest-labs', 1548084),
 ('deepseek-ai', 1448374),
 ('microsoft', 264891),
 ('unsloth', 142908),
 ('openbmb', 135782)]
```

## Version 1.0 Notes

- Working with complex objects (combinations of nested array-like and dictionary-like objects) 
might benefit from an abstraction that treats everything as an array thru the data pipeline.
Version 1.0 focused primarily on
the core objects being either list, dict, or SimpleNamespace. And in many cases, type normalization revealed itself as an issue.
- This project draws a lot of inspiration from LINQ. But while python is a dynamic language, I lean towards favoring
convenience in accessing the data. Mainly in the context of exploring the data from a console with the shortest amount of typing.
For example, select(lambda x: x.models.widgetOutputUrls) could access multiple arrays
and flatmap the result automatically.
  - Select implemented a unique feature, it passes a Ghost object into the lambda which collects the names of the
properties accessed. So from the previous example, the ghost would return an array like ['models', 'widgetOutputUrls'].
And this could inspire work for query compilation models, graph processing, etc.
- A small effort was made to add type signatures for the extensions api. The majority of signatures are heavily based on callable generics.
Although I removed them shortly after speculating that my pycharm editor could be glitching out because of something there...
- Version 2.0 should prioritize:
  - common data abstraction
  - plugin architecture
  - further exploring type annotation



## Testing
pytest 7.4.3

## Misc
Python 3.12.8

No dependencies outside of core python
