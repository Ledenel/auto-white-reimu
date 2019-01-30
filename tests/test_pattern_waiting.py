import pytest

from mahjong.container.pattern.reasoning import PatternMatchWaiting, HeuristicPatternMatchWaiting
from mahjong.container.pattern.win import NormalTypeWin
from mahjong.container.set import TileSet
from mahjong.container.utils import tile_set_from_string

hands = [
    "11266677788992m",
    "11246667778992m",
    "4677m2357p668s6z6s",
    "477m2357p668s46z6m",
    "79m899p24668s256z",
    "79m899p246689s256z",
]

shantens = [
    0,
    1,
    2,
    3,
    4,
    3,
]

usefuls = [
    "12m",
    "123789m",
    "5m1p4p6p",
    "5m7m1p4p6p6s7s",
    "8m6p7p8p9p1s2s3s4s5s6s7s8s9s2z5z6z",
]


@pytest.mark.parametrize("hand,shanten", zip(hands, shantens))
def test_pattern_waiting_step(hand, shanten):
    assert PatternMatchWaiting(NormalTypeWin
                               ()).before_waiting_step(tile_set_from_string(hand)) \
           == shanten


@pytest.mark.parametrize("hand,useful", zip(hands, usefuls))
def test_pattern_useful_tiles(hand, useful):
    assert TileSet(PatternMatchWaiting(NormalTypeWin()).useful_tiles(tile_set_from_string(hand))) \
           == tile_set_from_string(useful)


@pytest.mark.parametrize("hand,shanten", zip(hands, shantens))
def test_heuristic_waiting_step(hand, shanten):
    assert HeuristicPatternMatchWaiting(NormalTypeWin
                                        ()).before_waiting_step(tile_set_from_string(hand)) \
           == shanten


@pytest.mark.parametrize("hand,useful", zip(hands, usefuls))
def test_heuristic_useful_tiles(hand, useful):
    assert TileSet(HeuristicPatternMatchWaiting(NormalTypeWin()).useful_tiles(tile_set_from_string(hand))) \
           == tile_set_from_string(useful)
