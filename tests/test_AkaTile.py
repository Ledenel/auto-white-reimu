from unittest import TestCase

from mahjong.record.utils.value.tile import tile_from_tenhou
from mahjong.tile.definition import AkaTile, Tile


class TestTile(TestCase):
    def test_tile_from_tenhou(self):
        assert tile_from_tenhou(16) == tile_from_tenhou(17)
        assert tile_from_tenhou(52) == tile_from_tenhou(53)
        assert tile_from_tenhou(88) == tile_from_tenhou(89)
        assert {tile_from_tenhou(16) == tile_from_tenhou(17)}
        assert {tile_from_tenhou(52) == tile_from_tenhou(53)}
        assert {tile_from_tenhou(88) == tile_from_tenhou(89)}

    def test_AkaTile_Tile(self):
        assert AkaTile(0, 'm').next() == Tile(6, 'm')
        assert AkaTile(0, 'm') <= Tile(6, 'm')
        assert AkaTile(0, 'm') != Tile(6, 'm')
        assert AkaTile(0, 'm') >= Tile(4, 'm')
        assert AkaTile(0, 's').next() == Tile(6, 's')
        assert AkaTile(0, 's') <= Tile(6, 's')
        assert AkaTile(0, 's') != Tile(6, 's')
        assert AkaTile(0, 's') >= Tile(4, 's')
        assert AkaTile(0, 'p').next() == Tile(6, 'p')
        assert AkaTile(0, 'p') <= Tile(6, 'p')
        assert AkaTile(0, 'p') != Tile(6, 'p')
        assert AkaTile(0, 'p') >= Tile(4, 'p')

    def test_assert_errot(self):
        self.assertRaises(AssertionError, AkaTile, 1, 'm')
        self.assertRaises(AssertionError, AkaTile, 1, 's')
        self.assertRaises(AssertionError, AkaTile, 1, 'p')
        self.assertRaises(AssertionError, AkaTile, 0, 'z')
