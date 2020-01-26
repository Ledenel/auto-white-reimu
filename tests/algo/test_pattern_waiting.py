import pytest

from mahjong.container.pattern.reasoning import PatternMatchWaiting
from mahjong.container.pattern.win import NormalTypeWin
from mahjong.container.set import TileSet
from mahjong.container.utils import tile_set_from_string

hands = [
    "11266677788992m",
    "11246667778992m",
    "4677m2357p668s6z6s",
]

shantens = [
    0,
    1,
    2,
]

usefuls = [
    "12m",
    "123789m",
    "5m1p4p6p",
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
