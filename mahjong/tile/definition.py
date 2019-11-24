from __future__ import annotations

from functools import total_ordering
from typing import Optional

from ..container.set import TileSet

_suit_ordering = {
    'm': 0,
    'p': 1,
    's': 2,
    'z': 3,
}


def tile_hash_num(color: str, number: int) -> int:
    return _suit_ordering[color] * 10 + number


@total_ordering
class Tile:
    SUIT = set("mps")
    HONOR = set("z")
    SUIT_MIN = 1
    SUIT_MAX = 9
    FLUSH_LENGTH = 3
    TRIPLET_LENGTH = 3
    PAIR_LENGTH = 2

    _TILE_POOL = {}

    def __new__(cls, number: int, color: str):
        tile_hash = tile_hash_num(color, number)
        if tile_hash in Tile._TILE_POOL:
            return Tile._TILE_POOL[tile_hash]
        else:
            tile_obj = object.__new__(cls)
            self = tile_obj
            self._hash = tile_hash
            self._number = number
            self._color = color
            self._tuple_view = (color, number)
            Tile._TILE_POOL[tile_hash] = tile_obj
            self._flush = TileSet(
                (Tile(self._number + i, self._color) for i in range(Tile.FLUSH_LENGTH))
            ) if self.is_suit() and self._number <= Tile.SUIT_MAX - Tile.FLUSH_LENGTH + 1 else None
            self._triplet = self.repeat(Tile.TRIPLET_LENGTH)
            self._pair = self.repeat(Tile.PAIR_LENGTH)
            return tile_obj

    def __hash__(self):
        return self._hash

    def __eq__(self, other: Tile):
        return self._tuple_view == other._tuple_view

    def __ne__(self, other: Tile):
        return self._tuple_view != other._tuple_view

    def __lt__(self, other: Tile):
        return self._tuple_view < other._tuple_view

    def __init__(self, number: int, color: str):
        pass

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
        # if self.is_suit() and self._number <= Tile.SUIT_MAX - Tile.FLUSH_LENGTH + 1:
        #     return TileSet(
        #         (Tile(self._number + i, self._color) for i in range(Tile.FLUSH_LENGTH))
        #     )
        return self._flush

    def repeat(self, count: int) -> TileSet:
        return TileSet(
            (Tile(self._number, self._color) for _ in range(count))
        )

    def triplet(self) -> TileSet:
        # return self.repeat(Tile.TRIPLET_LENGTH)
        return self._triplet

    def pair(self) -> TileSet:
        # return self.repeat(Tile.PAIR_LENGTH)
        return self._pair

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


class AkaTile(Tile):
    _ATILE_POOL = {}

    def __new__(cls, number: int, color: str):
        assert 0 == number
        assert color in 'mps'
        tile_hash = tile_hash_num(color, number)
        if tile_hash in AkaTile._ATILE_POOL:
            return AkaTile._ATILE_POOL[tile_hash]
        else:
            tile_hash = tile_hash_num(color, number + 5)
            tile_obj = object.__new__(cls)
            self = tile_obj
            self._hash = tile_hash
            self._number = number
            self._color = color
            self._tuple_view = (color, number + 5)
            AkaTile._ATILE_POOL[tile_hash] = tile_obj
            self._flush = TileSet(
                (Tile(self._number + 5 + i, self._color) for i in range(Tile.FLUSH_LENGTH))
            ) if self.is_suit() and self._number == 0 else None
            self._triplet = self.repeat(Tile.TRIPLET_LENGTH)
            self._pair = self.repeat(Tile.PAIR_LENGTH)
            return tile_obj

    def next(self) -> Tile:
        if self.is_suit() and self._number < Tile.SUIT_MAX:
            return Tile(self._number + 6, self._color)

    def __init__(self, number: int, color: str):
        super().__init__(number, color)
        pass

    def __hash__(self):
        return self._hash

    def repeat(self, count: int) -> TileSet:
        return TileSet(
            (Tile(self._number + 5, self._color) for _ in range(count))
        )
