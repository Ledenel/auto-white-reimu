from abc import ABCMeta, abstractmethod
from itertools import count, product, chain
from typing import List

from mahjong.container.distribution import TileDistribution
from mahjong.container.pattern.win import WinPattern
from mahjong.container.set import TileSet
from mahjong.tile.definition import Tile


class Waiting(metaclass=ABCMeta):
    def __init__(self, win_pattern: WinPattern):
        self.win_pattern = win_pattern

    @abstractmethod
    def before_waiting_step(self, hand, ignore_4counts=True):
        pass

    @abstractmethod
    def useful_tiles(self, hand, ignore_4counts=True):
        pass

    def waiting_and_useful_tiles(self, hand, ignore_4counts=True):
        return self.before_waiting_step(hand, ignore_4counts), self.useful_tiles(hand, ignore_4counts)


class BruteForceWaiting(Waiting):

    def before_waiting_step(self, hand: TileSet, ignore_4counts=True) -> int:
        if self.win_pattern.match(hand):
            return -1
        for need_tiles in count(1):
            for tiles in product(TileDistribution.ALL_TILES, repeat=need_tiles):
                added_hand = hand + TileSet(tiles)
                if (ignore_4counts and all(v <= 4 for v in added_hand.values())) and self.win_pattern.match(added_hand):
                    return need_tiles - 1

    def useful_tiles(self, hand: TileSet, ignore_4counts=True):
        self_waiting = self.before_waiting_step(hand)
        return set(tile for tile in TileDistribution.ALL_TILES if
                   (ignore_4counts and hand[tile] < 4) and
                   self.before_waiting_step(hand + TileSet([tile])) < self_waiting)


def borrowed_limit(hand):
    borrow_limit = hand.copy()
    hand.re_sort()
    for tile in TileDistribution.ALL_TILES:
        borrow_limit[tile] -= 4
    return borrow_limit


class PatternMatchWaiting(Waiting):
    def __init__(self, win_pattern: WinPattern):
        super().__init__(win_pattern)

    def _win_selections_in_tiles(self, hand: TileSet, max_used_tiles_count, ignore_4counts, current_state: WinPattern,
                                 borrow_limits: TileSet, searching_start: List[Tile]):
        if sum((-hand).values()) > max_used_tiles_count:
            return
        if ignore_4counts and not all(cnt >= borrow_limits[tile] for tile, cnt in hand.items()):
            return
        if current_state.has_win():
            yield [], TileSet(-hand)
        if current_state.need_count() > sum((+hand).values()) + max_used_tiles_count:
            return
        hand = hand.copy()
        for tile in searching_start.copy():
            for unit, state in current_state.next_states(tile):
                hand_temp = hand.copy()
                hand_temp.subtract(unit)
                yield from (([unit] + tail, remains) for tail, remains in
                            self._win_selections_in_tiles(hand_temp, max_used_tiles_count, ignore_4counts, state,
                                                          borrow_limits, searching_start.copy()))
            if hand[tile] >= 0:
                del hand[tile]
            searching_start.remove(tile)

    def waiting_and_useful_tiles(self, hand, ignore_4counts=True):
        borrow_limit = borrowed_limit(hand)

        for need_tile_count in count(0):
            useful_tiles = set()
            for pattern, borrowed in self._win_selections_in_tiles(hand, need_tile_count, ignore_4counts,
                                                                   self.win_pattern, borrow_limit,
                                                                   TileDistribution.ALL_TILES.copy()):
                useful_tiles.update(borrowed)
            if len(useful_tiles) > 0:
                return need_tile_count - 1, useful_tiles

    def useful_tiles(self, hand: TileSet, ignore_4counts=True):
        _, useful_tiles = self.waiting_and_useful_tiles(hand, ignore_4counts)
        return useful_tiles

    def before_waiting_step(self, hand: TileSet, ignore_4counts=True) -> int:
        borrow_limit = borrowed_limit(hand)

        for need_tile_count in count(0):
            for pattern, borrowed in self._win_selections_in_tiles(hand, need_tile_count, ignore_4counts,
                                                                   self.win_pattern, borrow_limit,
                                                                   TileDistribution.ALL_TILES.copy()):
                return need_tile_count - 1


def borrowed_tile_count(hand):
    return sum((-hand).values())


class HeuristicPatternMatchWaiting(Waiting):
    def __init__(self, win_pattern: WinPattern):
        super().__init__(win_pattern)
        self.max_used_tiles = 0
        self.borrowed_count = None

    def before_waiting_step(self, hand: TileSet, ignore_4counts=True):
        self.max_used_tiles = sum(hand.values())
        result_iter = self._win_selections_in_tiles(hand, ignore_4counts, self.win_pattern, borrowed_limit(hand),
                                                    TileDistribution.ALL_TILES)
        return min(result_iter) - 1

    def useful_tiles(self, hand: TileSet, ignore_4counts=True):
        self_waiting = self.before_waiting_step(hand)
        return set(tile for tile in TileDistribution.ALL_TILES if
                   (ignore_4counts and hand[tile] < 4) and
                   self.before_waiting_step(hand + TileSet([tile])) < self_waiting)

    def _win_selections_in_tiles(self, hand: TileSet, ignore_4counts, current_state: WinPattern,
                                 borrow_limits: TileSet, searching_start: List[Tile]):
        if borrowed_tile_count(hand) > self.max_used_tiles:
            return
        if ignore_4counts and not all(cnt >= borrow_limits[tile] for tile, cnt in hand.items()):
            return
        if current_state.has_win():
            borrowed = TileSet(-hand)
            borrowed_count = sum(borrowed.values())
            self.max_used_tiles = borrowed_count - 1
            yield borrowed_count
            return
        if current_state.need_count() > sum((+hand).values()) + self.max_used_tiles:
            return

        hand = hand.copy()
        basic_hand_borrowed = borrowed_tile_count(hand)

        for can_borrowed in range(current_state.max_unit_length() + 1):
            min_used_tiles = current_state.need_units() * can_borrowed
            searching_round = searching_start.copy()
            hand_round = hand.copy()
            for tile in searching_round.copy():
                for unit, state in current_state.next_states(tile):
                    if can_borrowed + basic_hand_borrowed <= self.max_used_tiles and min_used_tiles <= self.max_used_tiles:
                        hand_temp = hand_round.copy()
                        hand_temp.subtract(unit)
                        borrowed_new = borrowed_tile_count(hand_temp)
                        if borrowed_new - basic_hand_borrowed == can_borrowed:
                            yield from (cnt for cnt in self._win_selections_in_tiles(hand_temp, ignore_4counts, state,
                                                                                     borrow_limits,
                                                                                     searching_round.copy()))
                    else:
                        return
