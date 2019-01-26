from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Optional, Iterator, Iterable, Tuple

from ...tile.definition import Tile
from ..set import TileSet
from ..utils import distinct


class WinPattern(metaclass=ABCMeta):

    def match(self, hand: TileSet) -> bool:
        for _ in self.win_selections(hand):
            return True
        return False

    def win_selections(self, hand: TileSet) -> Iterator[List[TileSet]]:
        if self.has_win():
            yield []
        if self.need_count() > sum(hand.values()):
            return
        hand = hand.copy()

        possible_units = TileSet()

        unit_list = list(self.update_possible_units(hand, possible_units))

        possible_units &= hand
        hand = possible_units

        if self.need_count() > sum(hand.values()):
            return

        for tile, unit_tuples in unit_list:
            for unit, next_state in unit_tuples:
                yield from ([unit] + tail for tail in next_state.win_selections(hand - unit))
            del hand[tile]

        # for tile in list(hand.keys()):
        #     states = self.next_states(tile)
        #     if states is not None:
        #         for unit, next_state in states:
        #             excluded = hand.exclude(unit)
        #             if excluded is not None:
        #                 yield from ([unit] + tail for tail in next_state.win_selections(excluded))
        #     del hand[tile]

    def update_possible_units(self, hand, possible_units):
        for tile in list(hand.keys()):
            states = self.next_states(tile)
            states_list = []
            if states is not None:
                for unit, next_state in states:
                    if hand.contains(unit):
                        possible_units.update(unit)
                        states_list.append((unit, next_state))
            yield tile, states_list

    def unique_win_selections(self, hand: TileSet) -> Iterator[List[TileSet]]:
        return distinct((sorted(selection) for selection in self.win_selections(hand)))

    @abstractmethod
    def has_win(self) -> bool:
        return False

    @abstractmethod
    def next_states(self, tile: Tile) -> Optional[Iterable[Tuple[TileSet, WinPattern]]]:
        pass

    @abstractmethod
    def need_count(self) -> int:
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

    def need_count(self) -> int:
        return self._pairs * 2 + self._melds * 3
