from itertools import product

import pytest

from mahjong.record.category import SubCategory

categories = list(product(*(range(x) for x in [2, 3, 4])))

indexes = list(range(2 * 3 * 4))


@pytest.mark.parametrize("cat,index", zip(categories, indexes))
def test_category(cat, index):
    category = SubCategory(2, 3, 4)
    assert category.category(index) == cat


@pytest.mark.parametrize("cat,index", zip(categories, indexes))
def test_index(cat, index):
    category = SubCategory(2, 3, 4)
    assert category.index(cat) == index


@pytest.mark.parametrize("cat,index", zip(categories, indexes))
def test_named_category(cat, index):
    category = SubCategory(2, 3, 4, caption="test", names=["a", "b", "c"])
    named = category.category(index)
    a, b, c = cat
    assert named.a == a
    assert named.b == b
    assert named.c == c
