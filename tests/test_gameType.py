import pytest

from mahjong.record.utils.value.gametype import GameType

types = [
    '169',
]

strs = [
    '四鳳南喰赤'
]


@pytest.mark.parametrize('typ,display', zip(types, strs))
def test_game_type_display(typ, display):
    assert str(GameType(typ)) == display
