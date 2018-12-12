from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Callable, Optional, Iterator, Iterable, Tuple

from tile.tile import Tile
from tile.set import TileSet
from tile.utils import distinct


class WinPattern(metaclass=ABCMeta):

    def match(self, hand: TileSet) -> bool:
        for _ in self.win_selections(hand):
            return True
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
    def has_win(self) -> bool:
        return False

    @abstractmethod
    def next_states(self, tile: Tile) -> Optional[Iterable[Tuple[TileSet, WinPattern]]]:
        pass


class NormalTypeWin(WinPattern):
    def __init__(self, pairs: int = 1, melds: int = 4):
        super().__init__()
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
