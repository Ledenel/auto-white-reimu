from functools import reduce


class SubCategory:
    def __init__(self, *total_num_of_each_category) -> None:
        super().__init__()
        self._totals = list(total_num_of_each_category)
        assert all(x > 0 for x in self._totals[1:])
        head = self._totals[0]
        assert head == -1 or head > 0
        self._totals.reverse()
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
        return tuple(cat_list)

    def index(self, category_tuple):
        assert len(category_tuple) == len(self._totals)
        index = category_tuple[0]
        for idx, total in zip(category_tuple[1:], self._totals[::-1][1:]):
            index *= total
            index += idx
        return index


TENHOU_TILE_CATEGORY = SubCategory(4, 9, 4)
