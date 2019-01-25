from unittest import TestCase

import pytest

from record.category import SubCategory, MixedCategory

categories = [
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 0),
    (1, 1),
    (2, 0),
    (2, 1),
    (2, 2),
    (2, 3)
]

indexes = list(range(len(categories)))

names = "aaabbcccc"


def init_normal():
    a, b, c = SubCategory(3), SubCategory(2), SubCategory(4)
    return MixedCategory([a, b, c])


def init_named():
    a, b, c = SubCategory(3, caption='a_sub', names=["a"]), \
              SubCategory(2, caption="b_sub", names=["b"]), \
              SubCategory(4, caption="c_sub", names=["c"])
    return MixedCategory([a, b, c], caption="mixed_cat", field_name="mixed")


@pytest.mark.parametrize("cat,index", zip(categories, indexes))
def test_category(cat, index):
    assert init_normal().category(index) == cat


@pytest.mark.parametrize("cat,index", zip(categories, indexes))
def test_index(cat, index):
    assert init_normal().index(cat) == index


@pytest.mark.parametrize("cat,index,name", zip(categories, indexes, names))
def test_named_category(cat, index, name):
    cat_outed = init_named().category(index)
    mix, v = cat_outed
    assert cat_outed.mixed == mix
    assert getattr(cat_outed, name) == v
