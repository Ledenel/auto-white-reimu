from __future__ import annotations

import random
from abc import abstractmethod
from collections import Iterator, Counter
from numbers import Number

from .set import TileSet
from ..tile.definition import Tile
from .utils import tile_set_from_string


class TileDistribution:
    ALL_TILES = list(tile_set_from_string("123456789m123456789p123456789s1234567z").keys())

    def weights(self):
        return [self.weight_of(tile) for tile in TileDistribution.ALL_TILES]

    @abstractmethod
    def weight_of(self, tile: Tile) -> Number:
        pass

    @abstractmethod
    def pick(self, tile: Tile) -> TileDistribution:
        pass

    def sample(self, count: int) -> Iterator[Tile]:
        current = self
        for i in range(count):
            next_item, *_ = random.choices(TileDistribution.ALL_TILES, current.weights())
            # print(next_item)
            yield next_item
            current = current.pick(next_item)


class StaticWall(TileDistribution):
    def __init__(self, tiles: TileSet):
        self._tiles = tiles

    def weight_of(self, tile: Tile) -> Number:
        return self._tiles[tile]

    def pick(self, tile: Tile) -> TileDistribution:
        return StaticWall(self._tiles - Counter([tile]))
