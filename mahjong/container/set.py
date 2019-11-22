from __future__ import annotations

from collections import Counter
from functools import total_ordering
from itertools import groupby
from typing import Iterator


@total_ordering
class TileSet(Counter):
    def re_sort(self):
        re_sorted = sorted(self.items())
        # print('resorted:', re_sorted)
        self.clear()
        for k, v in re_sorted:
            self[k] = v

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contains(self, tiles: TileSet) -> bool:
        for tile, count in tiles.items():
            if self[tile] < count:
                return False
        return True

    def _gen_str_iter(self) -> Iterator[str]:
        for key, group in groupby(self.items(), key=lambda tup: tup[0].color):
            for tile, num in group:
                yield str(tile.number) * num
            yield key

    def tiles(self):
        for tile, num in self.items():
            yield from [tile] * num

    def exclude(self, other):
        if self.contains(other):
            return self - other
        else:
            return None

    def __str__(self):
        self.re_sort()
        return ''.join(self._gen_str_iter())

    def __repr__(self):
        return "%s" % self

    def __len__(self):
        return sum(v for _, v in self.items())

    def __lt__(self, other: TileSet):
        return list(self.items()) < list(other.items())

    def __add__(self, other) -> TileSet:
        # tile_set = TileSet(super().__add__(other))
        # tile_set.re_sort()
        target = self.copy()
        target += other
        target.re_sort()
        return target

    def __sub__(self, other) -> TileSet:
        target = self.copy()
        target -= other
        return target

    def __and__(self, other) -> TileSet:
        return TileSet(super().__and__(other))

    def __or__(self, other) -> TileSet:
        return TileSet(super().__or__(other))
