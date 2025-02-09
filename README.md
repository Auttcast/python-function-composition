## Guide

### Composition with |

g(f(x)) == (f | g)(x)

To achieve inline composition, functions must be wrapped with the Composable object (f)

```python
from auttcomp.extensions import Api as f

square = f(lambda x: x ** 2)
add3 = f(lambda x: x + 3)

comp = square | add3
assert comp(3) == 12
```

### Automatic wrapping

If the composition chain starts with a Composable, the rest of the chain is automatically wrapped

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
pmap = f(map) & square

assert list(pmap([1, 2, 3])) == [1, 4, 9]
```

### Identity functions and invocation with >

When Composable receives a non-callable type, it constructs an identity function for that data

```python
from auttcomp.extensions import Api as f
from auttcomp.testing.testBase import getHuggingFaceSample

data = getHuggingFaceSample()

idFunc = f(data.models)
justDataModelsAgain = idFunc()
```

The data in this sample is a search result from the Hugging Face api. 

We'll explore the data with a query soon, but first we'd like to know about it's structure. It's difficult to understand the structure of the model just by looking at the raw data, so we'll use the f.shape function to help us understand it.

The f.shape function accepts any data as input, and prints a summary to the console.

When the invocation operator (>) is used, the identity function on the left is invoked first (returning data), and the data is passed as an argument into f.shape

```python
f(data.models) > f.shape
```

Result:

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

However, for convenience, many common functions have been curried and attached to f. So the same query could also be described as...

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

Next, map to tuple of (key, sumDownloads)

```python
(
  f(data.models)
  > f.group(lambda x: x.author)
  | f.map(lambda g: (
      g.key,
      f(g.value) > f.map(lambda x: x.downloads) | sum
  ))
  | list 
  | f.shape
)
```
```python
[('str', 'int')]
```

Finally, sort by descending downloads and take the top 5 results

```python
(
  f(data.models)
  > f.group(lambda x: x.author)
  | f.map(lambda g: (
    g.key,
    f(g.value) > f.map(lambda x: x.downloads) | sum
  ))
  | f.sortByDescending(lambda x: x[1])
  | f.take(5)
  | list
)
```
```python
[('black-forest-labs', 1548084),
 ('deepseek-ai', 1448374),
 ('microsoft', 264891),
 ('unsloth', 142908),
 ('openbmb', 135782)]
```

## Testing
pytest 7.4.3

## Misc
developed on Python 3.12.8

No dependencies outside of core python
