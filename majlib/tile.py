from __future__ import annotations

import bisect
import re
from abc import ABCMeta, abstractmethod
from collections import Counter
from functools import total_ordering
from itertools import groupby

from typing import List, Callable, Optional, Tuple, Iterable, Any, Type, Iterator


@total_ordering
class Tile:
    SUIT = set("mps")
    HONOR = set("z")
    SUIT_MIN = 1
    SUIT_MAX = 9
    FLUSH_LENGTH = 3
    TRIPLET_LENGTH = 3
    PAIR_LENGTH = 2

    def __hash__(self):
        return hash(self._tuple_view)

    def __eq__(self, other: Tile):
        return self._tuple_view == other._tuple_view

    def __ne__(self, other: Tile):
        return self._tuple_view != other._tuple_view

    def __lt__(self, other: Tile):
        return self._tuple_view < other._tuple_view

    def __init__(self, number: int, color: str):
        self._number = number
        self._color = color
        self._tuple_view = (color, number)

    def is_suit(self):
        return self._color in Tile.SUIT

    @property
    def color(self):
        return self._color

    @property
    def number(self):
        return self._number

    def next(self) -> Tile:
        if self.is_suit() and self._number < Tile.SUIT_MAX:
            return Tile(self._number + 1, self._color)

    def flush(self) -> Optional[TileSet]:
        if self.is_suit() and self._number <= Tile.SUIT_MAX - Tile.FLUSH_LENGTH + 1:
            return TileSet(
                (Tile(self._number + i, self._color) for i in range(Tile.FLUSH_LENGTH))
            )

    def repeat(self, count: int) -> TileSet:
        return TileSet(
            (Tile(self._number, self._color) for _ in range(count))
        )

    def triplet(self) -> TileSet:
        return self.repeat(Tile.TRIPLET_LENGTH)

    def pair(self) -> TileSet:
        return self.repeat(Tile.PAIR_LENGTH)

    def __str__(self) -> str:
        return str(self._number) + str(self._color)

    def __repr__(self) -> str:
        return '<%s>' % self


def tile_pair(tile: Tile) -> TileSet:
    return tile.pair()


def tile_triplet(tile: Tile) -> TileSet:
    return tile.triplet()


def tile_flush(tile: Tile) -> TileSet:
    return tile.flush()


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
        self.re_sort()

    def contains(self, tiles: TileSet):
        for tile, count in tiles.items():
            if self[tile] < count:
                return False
        return True

    def _gen_str_iter(self) -> Iterator[str]:
        for key, group in groupby(self.items(), key=lambda tup: tup[0].color):
            for tile, num in group:
                yield str(tile.number) * num
            yield key

    def __str__(self):
        return ''.join(self._gen_str_iter())

    def __repr__(self):
        return "%s" % self

    def __lt__(self, other: TileSet):
        return list(self.items()) < list(other.items())

    def __add__(self, other):
        return TileSet(super().__add__(other))

    def __sub__(self, other):
        return TileSet(super().__sub__(other))

    def __and__(self, other):
        return TileSet(super().__and__(other))

    def __or__(self, other):
        return TileSet(super().__or__(other))


_tile_group_regex = re.compile(r"[0-9]+[%s]" % (''.join(Tile.SUIT | Tile.HONOR)))


def tile_set_from_string(token: str) -> TileSet:
    return TileSet(tiles_from_string(token))


def tiles_from_string(token: str) -> Iterable[Tile]:
    for group in _tile_group_regex.finditer(token):
        group_value = group.group(0)
        numbers, color = group_value[:-1], group_value[-1]
        yield from (Tile(int(number), color) for number in numbers)


def distinct(iterable: Iterable):
    unique = []
    for item in iterable:
        index = bisect.bisect_left(unique, item)
        if index >= len(unique) or unique[index] != item:
            yield item
            unique.insert(index, item)


class WinPattern(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self._tile_unit_selections: List[Callable[[Tile], Optional[TileSet]]] = []

    def match(self, hand: TileSet) -> bool:
        if self.has_win():
            return True

        for tile in hand:
            for tile_unit_picker in self._tile_unit_selections:
                tile_unit = tile_unit_picker(tile)
                if tile_unit and hand.contains(tile_unit):
                    next_win = self.next_win_state(tile_unit, tile_unit_picker)
                    if next_win:
                        if next_win.match(hand - tile_unit):
                            return True
                    else:
                        return False

        return False

    def win_selections(self, hand: TileSet) -> Iterator[List[TileSet]]:
        if self.has_win():
            yield []
        for tile in list(hand.keys()):
            states = self.next_states(tile)
            if states is not None:
                for unit, next_state in states:
                    if hand.contains(unit):
                        yield from ([unit] + tail for tail in next_state.win_selections(hand - unit))
            del hand[tile]

    def unique_win_selections(self, hand: TileSet) -> Iterator[List[TileSet]]:
        return distinct((sorted(selection) for selection in self.win_selections(hand)))

    @abstractmethod
    def next_win_state(self, piece: TileSet, pick_func: Callable[[Tile], Optional[TileSet]]) -> Optional[WinPattern]:
        return self

    @abstractmethod
    def has_win(self) -> bool:
        return False

    @abstractmethod
    def next_states(self, tile: Tile) -> Optional[Iterable[Tuple[TileSet, WinPattern]]]:
        pass


class NormalTypeWin(WinPattern):
    def __init__(self, pairs: int = 1, melds: int = 4):
        super().__init__()
        self._tile_unit_selections = [tile_pair, tile_flush, tile_triplet]
        self._pairs = pairs
        self._melds = melds

    def has_win(self) -> bool:
        return self._pairs == 0 and self._melds == 0

    def next_states(self, tile: Tile) -> Optional[Iterable[Tuple[TileSet, WinPattern]]]:
        if self._pairs > 0:
            yield (tile.pair(), NormalTypeWin(self._pairs - 1, self._melds))

        if self._melds > 0:
            meld_next = NormalTypeWin(self._pairs, self._melds - 1)
            flush = tile.flush()
            if flush:
                yield (flush, meld_next)
            yield (tile.triplet(), meld_next)

    def next_win_state(self, piece: TileSet, pick_func: Callable[[Tile], Optional[TileSet]]) -> Optional[WinPattern]:
        if pick_func == tile_pair:
            return NormalTypeWin(max(self._pairs - 1, 0), self._melds)
        elif pick_func in [tile_flush, tile_triplet]:
            return NormalTypeWin(self._pairs, max(self._melds - 1, 0))
        else:
            raise ValueError(
                "Picking method %s is not one of (tile_pair, tile_flush, tile_triplet). Please check again." % (
                    pick_func))
