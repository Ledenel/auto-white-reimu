from unittest import TestCase

import pytest

from mahjong.record.category import SubCategory, MixedCategory
from mahjong.record.utils.constant import TENHOU_TILE_CATEGORY

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


tenhou_indexes = list(range(136))

tenhou_categories = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, 3), (0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 1, 3), (0, 2, 0),
                     (0, 2, 1), (0, 2, 2), (0, 2, 3), (0, 3, 0), (0, 3, 1), (0, 3, 2), (0, 3, 3), (0, 4, 0), (0, 4, 1),
                     (0, 4, 2), (0, 4, 3), (0, 5, 0), (0, 5, 1), (0, 5, 2), (0, 5, 3), (0, 6, 0), (0, 6, 1), (0, 6, 2),
                     (0, 6, 3), (0, 7, 0), (0, 7, 1), (0, 7, 2), (0, 7, 3), (0, 8, 0), (0, 8, 1), (0, 8, 2), (0, 8, 3),
                     (1, 0, 0), (1, 0, 1), (1, 0, 2), (1, 0, 3), (1, 1, 0), (1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 2, 0),
                     (1, 2, 1), (1, 2, 2), (1, 2, 3), (1, 3, 0), (1, 3, 1), (1, 3, 2), (1, 3, 3), (1, 4, 0), (1, 4, 1),
                     (1, 4, 2), (1, 4, 3), (1, 5, 0), (1, 5, 1), (1, 5, 2), (1, 5, 3), (1, 6, 0), (1, 6, 1), (1, 6, 2),
                     (1, 6, 3), (1, 7, 0), (1, 7, 1), (1, 7, 2), (1, 7, 3), (1, 8, 0), (1, 8, 1), (1, 8, 2), (1, 8, 3),
                     (2, 0, 0), (2, 0, 1), (2, 0, 2), (2, 0, 3), (2, 1, 0), (2, 1, 1), (2, 1, 2), (2, 1, 3), (2, 2, 0),
                     (2, 2, 1), (2, 2, 2), (2, 2, 3), (2, 3, 0), (2, 3, 1), (2, 3, 2), (2, 3, 3), (2, 4, 0), (2, 4, 1),
                     (2, 4, 2), (2, 4, 3), (2, 5, 0), (2, 5, 1), (2, 5, 2), (2, 5, 3), (2, 6, 0), (2, 6, 1), (2, 6, 2),
                     (2, 6, 3), (2, 7, 0), (2, 7, 1), (2, 7, 2), (2, 7, 3), (2, 8, 0), (2, 8, 1), (2, 8, 2), (2, 8, 3),
                     (3, 0, 0), (3, 0, 1), (3, 0, 2), (3, 0, 3), (3, 1, 0), (3, 1, 1), (3, 1, 2), (3, 1, 3), (3, 2, 0),
                     (3, 2, 1), (3, 2, 2), (3, 2, 3), (3, 3, 0), (3, 3, 1), (3, 3, 2), (3, 3, 3), (3, 4, 0), (3, 4, 1),
                     (3, 4, 2), (3, 4, 3), (3, 5, 0), (3, 5, 1), (3, 5, 2), (3, 5, 3), (3, 6, 0), (3, 6, 1), (3, 6, 2),
                     (3, 6, 3)]


@pytest.mark.parametrize("index,category", zip(tenhou_indexes, tenhou_categories))
def test_tenhou_tiles_to_category(index, category):
    assert TENHOU_TILE_CATEGORY.category(index) == category

@pytest.mark.parametrize("index,category", zip(tenhou_indexes, tenhou_categories))
def test_tenhou_tiles_to_index(index, category):
    assert TENHOU_TILE_CATEGORY.index(category) == index