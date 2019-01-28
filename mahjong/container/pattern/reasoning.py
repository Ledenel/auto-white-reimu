from itertools import count, product

from mahjong.container.distribution import TileDistribution
from mahjong.container.pattern.win import WinPattern
from mahjong.container.set import TileSet


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

        return min(self.before_waiting_step(hand + TileSet([tile])) for tile in TileDistribution.ALL_TILES) + 1

    def useful_tiles(self, hand: TileSet, ignore_4counts=True):
        self_waiting = self.before_waiting_step(hand)
        return list(tile for tile in TileDistribution.ALL_TILES if
                    (ignore_4counts and hand[tile] < 4) and
                    self.before_waiting_step(hand + TileSet([tile])) < self_waiting)
