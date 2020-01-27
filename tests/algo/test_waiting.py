import pytest

from mahjong.container.pattern.reasoning import BruteForceWaiting
from mahjong.container.pattern.win import NormalTypeWin
from mahjong.container.set import TileSet
from mahjong.container.utils import tile_set_from_string

hands = [
    "11246667778992m",
    "112466677788992m",
]

shantens = [
    1,
    0
]

usefuls = [
    "123789m"
]


@pytest.mark.parametrize("hand,shanten", zip(hands, shantens))
def test_waiting_step(hand, shanten):
    assert BruteForceWaiting(NormalTypeWin()).before_waiting_step(tile_set_from_string(hand)) \
           == shanten


@pytest.mark.parametrize("hand,useful", zip(hands, usefuls))
def test_useful_tiles(hand, useful):
    assert TileSet(BruteForceWaiting(NormalTypeWin()).useful_tiles(tile_set_from_string(hand))) \
           == tile_set_from_string(useful)


