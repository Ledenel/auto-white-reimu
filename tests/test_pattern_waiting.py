import pytest

from mahjong.container.pattern.reasoning import PatternMatchWaiting
from mahjong.container.pattern.win import NormalTypeWin
from mahjong.container.set import TileSet
from mahjong.container.utils import tile_set_from_string


hands = [
    "11246667778992m",
    "11266677788992m",
    "477m2357p668s46z6m",
]

shantens = [
    1,
    0,
    3,
]

usefuls = [
    "123789m",
    "12m",
    "5m7m1p4p6p6s7s",
]


@pytest.mark.parametrize("hand,useful", zip(hands, usefuls))
def test_useful_tiles(hand, useful):
    assert TileSet(PatternMatchWaiting(NormalTypeWin()).useful_tiles(tile_set_from_string(hand))) \
           == tile_set_from_string(useful)


@pytest.mark.parametrize("hand,shanten", zip(hands, shantens))
def test_pattern_waiting_step(hand, shanten):
    assert PatternMatchWaiting(NormalTypeWin()).before_waiting_step(tile_set_from_string(hand))\
           == shanten