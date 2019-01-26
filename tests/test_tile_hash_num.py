from unittest import TestCase

from mahjong.container.utils import tiles_from_string


class TestTileHashNum(TestCase):
    def test_unique_tile_hash_num(self):
        all_tiles = tiles_from_string("123456789s123456789m123456789p1234567z")
        tile_duplicated_hash = list(hash(x) for x in all_tiles)
        tile_unique = set(tile_duplicated_hash)
        assert len(tile_unique) == len(tile_duplicated_hash)
