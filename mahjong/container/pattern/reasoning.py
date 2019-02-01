import logging
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from itertools import count, product, chain, groupby
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


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def need_to_borrow(hand: TileSet, unit: TileSet):
    hand = hand.copy()
    hand.subtract(unit)
    return borrowed_tile_count(hand)


class HeuristicPatternMatchWaiting(Waiting):
    def __init__(self, win_pattern: WinPattern):
        super().__init__(win_pattern)
        self.max_used_tiles = 0
        self.borrowed_count = None

    def before_waiting_step(self, hand: TileSet, ignore_4counts=True):
        self.max_used_tiles = sum(hand.values())

        borrows = self.init_search_by_hand(hand)

        result_iter = self._win_selections_in_tiles(hand, ignore_4counts, self.win_pattern, borrowed_limit(hand),
                                                    borrows, 0, 1)
        return min(v for v, _, _ in result_iter) - 1

    def init_search_by_hand(self, hand):
        units = [(need_to_borrow(hand, unit), tile, unit) for tile in
                 TileDistribution.ALL_TILES for unit, _ in self.win_pattern.next_states(tile)]
        units.sort()
        borrowed_count_map = defaultdict(
            list,
            {borrow_count: list(group) for borrow_count, group in groupby(units, lambda x: x[0])}
        )
        borrows = [
            sorted(set(tile
                       for i in range(searching_borrow, -1, -1)
                       for _, tile, _ in borrowed_count_map[i]))
            for searching_borrow in range(self.win_pattern.max_unit_length() + 1)
        ]
        return borrows

    def useful_tiles(self, hand: TileSet, ignore_4counts=True):
        _, useful = self.waiting_and_useful_tiles(hand, ignore_4counts)
        return useful

    def waiting_and_useful_tiles(self, hand, ignore_4counts=True):
        logging.debug("finding waiting step")
        self_waiting = self.before_waiting_step(hand)
        borrows = self.init_search_by_hand(hand)
        self.max_used_tiles = self_waiting + 1
        logging.debug("finding useful tiles")
        result_iter = self._win_selections_in_tiles(hand, ignore_4counts, self.win_pattern, borrowed_limit(hand),
                                                    borrows, 0, 0)

        return self_waiting, set(tile for _, _, borrows in result_iter for tile in borrows)

    def _win_selections_in_tiles(self, hand: TileSet, ignore_4counts, current_state: WinPattern,
                                 borrow_limits: TileSet, searching_group: List[List[Tile]], borrowed_stage,
                                 waiting_step_pruning):
        # if borrowed_tile_count(hand) > self.max_used_tiles:
        #     return
        if ignore_4counts and not all(cnt >= borrow_limits[tile] for tile, cnt in hand.items()):
            return
        if current_state.has_win():
            borrowed = TileSet(-hand)
            borrowed_count = sum(borrowed.values())
            self.max_used_tiles = borrowed_count - waiting_step_pruning
            logging.debug("found borrowing %s", borrowed)
            yield borrowed_count, [], borrowed
            return
        # if current_state.need_count() > sum((+hand).values()) + self.max_used_tiles:
        #     return

        hand = hand.copy()
        basic_hand_borrowed = borrowed_tile_count(hand)

        for can_borrowed in range(borrowed_stage, current_state.max_unit_length() + 1):
            min_used_tiles = current_state.need_units() * can_borrowed
            searching_round_old = searching_group[can_borrowed]
            searching_round = searching_round_old.copy()
            temp_searching_group = searching_group.copy()
            temp_searching_group[can_borrowed] = searching_round
            hand_round = hand
            for tile in searching_round.copy():
                for unit, state in current_state.next_states(tile):
                    if basic_hand_borrowed + min_used_tiles <= self.max_used_tiles:
                        logging.debug("test %s in %s at borrow stage %d", unit, hand, can_borrowed)
                        hand_temp = hand_round.copy()
                        hand_temp.subtract(unit)
                        borrowed_new = borrowed_tile_count(hand_temp)
                        if borrowed_new - basic_hand_borrowed == can_borrowed:
                            logging.debug("search %s in %s borrowed %s", unit, hand, TileSet(-hand))
                            yield from ((cnt, [unit] + patterns, borrowed) for cnt, patterns, borrowed in
                                        self._win_selections_in_tiles(hand_temp, ignore_4counts, state,
                                                                      borrow_limits,
                                                                      temp_searching_group, can_borrowed,
                                                                      waiting_step_pruning))
                    else:
                        logging.debug("%s plan to borrowing out of range %d",
                                      hand,
                                      self.max_used_tiles - basic_hand_borrowed)
                        return
                searching_round.remove(tile)
