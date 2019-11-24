import bisect
import re
from typing import Iterable

from .set import TileSet
from ..tile.definition import Tile, AkaTile

_tile_group_regex = re.compile(r"[0-9]+[%s]|[1-7]+%s"
                               % (''.join(Tile.SUIT), ''.join(Tile.HONOR)))


def tiles_from_string(token: str) -> Iterable[Tile]:
    for group in _tile_group_regex.finditer(token):
        group_value = group.group(0)
        numbers, color = group_value[:-1], group_value[-1]
        yield from (Tile(int(number), color) if number != '0' else AkaTile(int(number), color) for number in numbers)


def tile_set_from_string(token: str) -> TileSet:
    tile_set = TileSet(tiles_from_string(token))
    tile_set.re_sort()
    return tile_set


def distinct(iterable: Iterable):
    unique = []
    for item in iterable:
        index = bisect.bisect_left(unique, item)
        if index >= len(unique) or unique[index] != item:
            yield item
            unique.insert(index, item)
