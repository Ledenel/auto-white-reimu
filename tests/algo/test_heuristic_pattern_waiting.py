import pytest

from mahjong.container.pattern.reasoning import HeuristicPatternMatchWaiting
from mahjong.container.pattern.win import NormalTypeWin, UniquePairs
from mahjong.container.set import TileSet
from mahjong.container.utils import tile_set_from_string

hands = [
    "11266677788992m",
    "11246667778992m",
    "4677m2357p668s6z6s",
    "477m2357p668s46z6m",
    "79m899p24668s256z",
    "79m899p246689s56z",
    "1115555s456m111z",
    "4677m2307p668s6z6s",
    "477m2307p668s46z6m",
    "1110555s406m111z",
]

seven_pair_shantens = [
    1,
    1,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4
]

shantens = [
    0,
    1,
    2,
    3,
    4,
    3,
    1,
    2,
    3,
    1,
]

usefuls = [
    "12m",
    "123789m",
    "5m1p4p6p",
    "5m7m1p4p6p6s7s",
    "8m6p7p8p9p1s2s3s4s5s6s7s8s9s2z5z6z",
    "8m7p9p3s6s7s",
    "1m2m3m4m5m6m7m8m9m1p2p3p4p5p6p7p8p9p2s3s4s6s7s8s9s2z3z4z5z6z7z",
    "5m1p4p6p",
    "5m7m1p4p6p6s7s",
    "1m2m3m4m5m6m7m8m9m1p2p3p4p5p6p7p8p9p2s3s4s6s7s8s9s2z3z4z5z6z7z",
]


@pytest.mark.parametrize("hand,shanten", zip(hands, shantens))
def test_heuristic_waiting_step(hand, shanten):
    assert HeuristicPatternMatchWaiting(NormalTypeWin
                                        ()).before_waiting_step(tile_set_from_string(hand)) \
           == shanten


@pytest.mark.parametrize("hand,shanten", zip(hands, seven_pair_shantens))
def test_heuristic_seven_pair_waiting_step(hand, shanten):
    assert HeuristicPatternMatchWaiting(UniquePairs()).before_waiting_step(tile_set_from_string(hand)) \
           == shanten


@pytest.mark.parametrize("hand,useful", zip(hands, usefuls))
def test_heuristic_useful_tiles(hand, useful):
    assert TileSet(HeuristicPatternMatchWaiting(NormalTypeWin()).useful_tiles(tile_set_from_string(hand))) \
           == tile_set_from_string(useful)
