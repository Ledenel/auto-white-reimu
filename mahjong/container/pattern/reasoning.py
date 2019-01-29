from itertools import count, product
from typing import List

from mahjong.container.distribution import TileDistribution
from mahjong.container.pattern.win import WinPattern
from mahjong.container.set import TileSet
from mahjong.tile.definition import Tile


class Waiting:
    def __init__(self, win_pattern: WinPattern):
        self.win_pattern = win_pattern

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

    def waiting_and_useful_tiles(self, hand, ignore_4counts=True):
        return self.before_waiting_step(hand, ignore_4counts), self.useful_tiles(hand, ignore_4counts)


class PatternMatchWaiting:
    def __init__(self, win_pattern: WinPattern):
        self.win_pattern = win_pattern

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

    def useful_tiles(self, hand: TileSet, ignore_4counts=True):
        borrow_limit = hand.copy()
        for tile in TileDistribution.ALL_TILES:
            borrow_limit[tile] -= 4

        for need_tile_count in count(0):
            useful_tiles = set()
            for pattern, borrowed in self._win_selections_in_tiles(hand, need_tile_count, ignore_4counts,
                                                                   self.win_pattern, borrow_limit,
                                                                   TileDistribution.ALL_TILES.copy()):
                useful_tiles.update(borrowed)
            if len(useful_tiles) > 0:
                return useful_tiles

    def before_waiting_step(self, hand: TileSet, ignore_4counts=True) -> int:
        borrow_limit = hand.copy()
        hand.re_sort()
        for tile in TileDistribution.ALL_TILES:
            borrow_limit[tile] -= 4

        for need_tile_count in count(0):
            for pattern, borrowed in self._win_selections_in_tiles(hand, need_tile_count, ignore_4counts,
                                                                   self.win_pattern, borrow_limit,
                                                                   TileDistribution.ALL_TILES.copy()):
                return need_tile_count - 1
