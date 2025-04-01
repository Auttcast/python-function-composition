from ..extensions import KeyValuePair, Api as f
from .base_test import get_hugging_face_sample, get_civitai_sample
from ..quicklog import tracelog

@tracelog("test_id")
def test_id():
    func = f.id(123)
    actual = func()
    assert actual == 123

@tracelog("test_at")
def test_at():
    data = {"foo": 123}
    actual = f.at(lambda x: x['foo'])(data)
    assert actual == 123

@tracelog("test_map")
def test_map():
    data = [1, 2, 3]
    gen = f.map(lambda x: x + 1)(data)
    actual = list(gen)
    assert actual == [2, 3, 4]

@tracelog("test_filter")
def test_filter():
    data = [1, 2, 3]
    gen = f.filter(lambda x: x % 2 == 0)(data)
    actual = list(gen)
    assert actual == [2]

@tracelog("test_reduce")
def test_reduce():
    data = [2, 2, 2]
    actual = f.reduce(lambda p, n: p + n)(data)
    assert actual == 6

@tracelog("test_reduce_initial")
def test_reduce_initial():
    data = [2, 2, 2]
    actual = f.reduce(lambda p, n: p + n, 2)(data)
    assert actual == 8

@tracelog("test_flatmap")
def test_flatmap():
    data = [[1], [1], [1]]
    gen = f.flatmap(lambda x: x)(data)
    actual = list(gen)
    assert actual == [1, 1, 1]

@tracelog("test_flatmap_id")
def test_flatmap_id():
    data = [[1], [1], [1]]
    gen = f.flatmap()(data)
    actual = list(gen)
    assert actual == [1, 1, 1]

@tracelog("test_reverse")
def test_reverse():
    data = [1, 2, 3]
    gen = f.reverse(data)
    actual = list(gen)
    assert actual == [3, 2, 1]

@tracelog("test_any")
def test_any():
    data1 = [0, 0, 0]
    data2 = [0, 0, 111]

    actual1 = f.any(lambda x: x == 111)(data1)
    actual2 = f.any(lambda x: x == 111)(data2)

    assert actual1 == False
    assert actual2 == True

@tracelog("test_all")
def test_all():
    data1 = [0, 0, 0]
    data2 = [0, 0, 111]

    actual1 = f.all(lambda x: x == 0)(data1)
    actual2 = f.all(lambda x: x == 0)(data2)

    assert actual1 == True
    assert actual2 == False
    
@tracelog("test_sort")
def test_sort():
    data = [2, 3, 1]
    gen = f.sort(data)
    actual = list(gen)
    assert actual == [1, 2, 3]

@tracelog("test_sort_by")
def test_sort_by():
    data = [
        {"id": 2},
        {"id": 3},
        {"id": 1}
    ]
    expected = [
        {"id": 1},
        {"id": 2},
        {"id": 3}
    ]

    gen = f.sort_by(lambda x: x['id'])(data)

    actual = list(gen)

    assert actual == expected

@tracelog("test_sort_by_desc")
def test_sort_by_desc():
    data = [
        {"id": 2},
        {"id": 3},
        {"id": 1}
    ]
    expected = [
        {"id": 3},
        {"id": 2},
        {"id": 1}
    ]

    gen = f.sort_by_desc(lambda x: x['id'])(data)

    actual = list(gen)

    assert actual == expected

@tracelog("test_take")
def test_take():
    data = [1, 2, 3]
    gen = f.take(2)(data)
    actual = list(gen)
    assert actual == [1, 2]

@tracelog("test_skip")
def test_skip():
    data = [1, 2, 3]
    gen = f.skip(1)(data)
    actual = list(gen)
    assert actual == [2, 3]

@tracelog("test_group")
def test_group():
    data = [
        {"id": 1, "tag": "TAG1"},
        {"id": 2, "tag": "TAG2"},
        {"id": 3, "tag": "TAG1"},
        {"id": 4, "tag": "TAG2"}
    ]

    expected = [
        KeyValuePair("TAG1", [
            {"id": 1, "tag": "TAG1"},
            {"id": 3, "tag": "TAG1"}
        ]),
        KeyValuePair("TAG2", [
            {"id": 2, "tag": "TAG2"},
            {"id": 4, "tag": "TAG2"}
        ])
    ]

    gen = f.group(lambda x: x['tag'])
    
    actual = list(gen(data))
    
    assert actual == expected


@tracelog("test_join")
def test_join():

    dataFoo = [
        {"foo_id": 1, "foo": "foo1"},
        {"foo_id": 2, "foo": "foo2"},
        {"foo_id": 50, "foo": "foo50"},
        {"foo_id": 3, "foo": "foo3"},
        {"foo_id": 4, "foo": "foo4"}
    ]

    dataBar = [
        {"bar_id": 1, "bar": "bar1"},
        {"bar_id": 2, "bar": "bar2"},
        {"bar_id": 3, "bar": "bar3"},
        {"bar_id": 4, "bar": "bar4"},
        {"bar_id": 100, "bar": "bar100"}
    ]

    expected = [
        (1, (["foo1"], ["bar1"])),
        (2, (["foo2"], ["bar2"])),
        (3, (["foo3"], ["bar3"])),
        (4, (["foo4"], ["bar4"]))
    ]
    
    gen = f.join(
        left_data=dataFoo,
        left_key_func=lambda x: x['foo_id'],
        right_key_func=lambda x: x['bar_id'],
        left_value_selector=lambda x: x['foo'],
        right_value_selector=lambda x: x['bar']
    )(dataBar)
    
    actual = list(gen)

    assert actual == expected

@tracelog("test_distinct_set")
def test_distinct_set():
    arr = f.id([1, 2, 3, 3, 3, 3])
    slow_distinct = arr > f.distinct
    fast_distinct = arr > f.distinct_set
    assert slow_distinct == fast_distinct


@tracelog("test_zip")
def test_zip():
    data1 = ["a", "b", "c"]
    data2 = ["A", "B"]
    expected = [("a", "A"),("b", "B"),("c", None)]

    gen = f.zip(data2)(data1)

    actual = list(gen)

    assert actual == expected

@tracelog("test_flatnest")
def test_flatnest():
    data = {
        "depth": 1,
        "nest": {
            "depth": 2,
            "nest": {
                "depth": 3,
                "nest": None
                }
            }
        }
    
    expected = [1, 2, 3]

    gen = f.flatnest(
        path_selector=lambda x: x['nest'],
        data_selector=lambda x: x['depth']
        )(data)

    actual = list(gen)

    assert actual == expected

@tracelog("test_first")
def test_first():
    data = [1, 1, 5]

    expected = 1

    actual = f.first(lambda x: x == 1)(data)

    assert actual == expected

@tracelog("test_first_none_if_no_match")
def test_first_none_if_no_match():
    data = [1, 1, 5]

    expected = None

    actual = f.first(lambda x: x == 10)(data)

    assert actual == expected

@tracelog("test_single")
def test_single():
    data = [1, 1, 5]

    expected = 5

    actual = f.single(lambda x: x == 5)(data)

    assert actual == expected

@tracelog("test_single_throw_if_more_than_one")
def test_single_throw_if_more_than_one():
    data = [1, 1, 5]

    try:
        f.single(lambda x: x == 1)(data)
        raise AssertionError("expected to throw ValueError because selector matches multiple items")
    except ValueError:
        pass

@tracelog("test_single_throw_if_no_match")
def test_single_throw_if_no_match():
    data = [1, 1, 5]

    try:
        f.single(lambda x: x == 10)(data)
        raise AssertionError("expected to throw ValueError because selector matches no items")
    except ValueError:
        pass

@tracelog("test_huggingface_sample")
def test_huggingface_sample():
    data = get_hugging_face_sample()
    
    result = f.id(data.models) > (
        f.group(lambda x: x.author)
        | f.map(lambda x: (
            x.key,
            f.id(x.value) > f.map(lambda x2: x2.downloads) | sum
        ))
        | f.sort_by_desc(lambda x: x[1])
        | f.take(3)
        | list
    )

    assert result == [('black-forest-labs', 1548084), ('deepseek-ai', 1448374), ('microsoft', 264891)]

@tracelog("test_civitai_sample")
def test_civitai_sample():
    data = get_civitai_sample()

    most_common_tags = f.id(data.result.data.json.collection.items) > (
        f.flatmap(lambda x: x.data.tagIds)
        | f.group()
        | f.map(lambda x: (
            x.key,
            f.id(x.value) > f(len)
        ))
        | f.sort_by_desc(lambda x: x[1])
        | f.map(lambda x: x[0])
        | f.take(3)
        | list
    )

    assert most_common_tags == [292, 81, 5262]
