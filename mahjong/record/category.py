import bisect
import math
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from functools import reduce
from typing import Iterable


class Category(metaclass=ABCMeta):
    @abstractmethod
    def category(self, index):
        pass

    @abstractmethod
    def index(self, category_tuple):
        pass

    @abstractmethod
    def __len__(self):
        pass


class MixedCategory(Category):
    def __init__(self, category_list: Iterable[Category], caption=None, names=None):
        self.category_list = list(category_list)
        assert all(len(c) < math.inf for c in self.category_list[:-1])
        self._named_tuple_class = namedtuple(caption, names) if names is not None else None
        self._max = sum(len(c) for c in self.category_list)
        self._accumulate_range = list(self._accumulate())

    def _accumulate(self):
        sum_len = 0
        yield sum_len
        for length in (len(c) for c in self.category_list):
            sum_len += length
            yield sum_len

    def __len__(self):
        return self._max

    def category(self, index):
        category = bisect.bisect_right(self._accumulate_range, index)
        sub_id = self.category_list[category - 1].category(index - self._accumulate_range[category])
        cat_list = [category - 1, sub_id]
        return tuple(cat_list) if self._named_tuple_class is None else self._named_tuple_class(*cat_list)

    def index(self, category_tuple):
        category, sub_id = category_tuple
        return self._accumulate_range[category] + sub_id


class SubCategory(Category):
    def __init__(self, *total_num_of_each_category, caption=None, names=None) -> None:
        super().__init__()
        self._totals = list(total_num_of_each_category)
        assert all(x > 0 for x in self._totals[1:])
        head = self._totals[0]
        assert head == -1 or head > 0
        self._totals.reverse()
        self._named_tuple_class = namedtuple(caption, names) if names is not None else None
        if head != -1:
            self._max = reduce(lambda x, y: x * y, self._totals)
        else:
            self._max = None

    def _category_iter(self, index):
        assert self._max is None or index < self._max
        for total in self._totals:
            if total != -1:
                yield index % total
                index //= total
            else:
                yield index

    def category(self, index):
        cat_list = list(self._category_iter(index))
        cat_list.reverse()
        return tuple(cat_list) if self._named_tuple_class is None else self._named_tuple_class(*cat_list)

    def index(self, category_tuple):
        assert len(category_tuple) == len(self._totals)
        index = category_tuple[0]
        for idx, total in zip(category_tuple[1:], self._totals[::-1][1:]):
            index *= total
            index += idx
        return index

    def __len__(self):
        return math.inf if self._max is None else self._max


TENHOU_TILE_CATEGORY = SubCategory(4, 9, 4)
