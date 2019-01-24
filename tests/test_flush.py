from unittest import TestCase

import pytest

from container.utils import tiles_from_string
from record.reader import tile_from_tenhou
from record.util import Flush

basic_data = ['9239', '33031', '13511', '26663', '58615', '50519', '26687', '25007', '39199', '62791', '62623', '9639',
              '59703']
answers = [
    '456m',
    '645p',
    '657m',
    '423p',
    '678s',
    '435s',
    '423p',
    '234p',
    '867p',
    '879s',
    '879s',
    '456m',
    '768s'
]


@pytest.mark.parametrize("data,answer", zip(basic_data, answers))
def test_self_tiles(data, answer):
    flush = Flush(0, data)
    tiles = list(tiles_from_string(answer))
    borrowed, *self_tiles = tiles
    assert {borrowed} == {tile_from_tenhou(x) for x in flush.borrowed_tiles}
    assert set(self_tiles) == {tile_from_tenhou(x) for x in flush.self_tiles}
