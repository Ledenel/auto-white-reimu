from unittest import TestCase

import tile


class TestTile(TestCase):
    def test_count(self):
        hand1 = tile.tile_set_from_string("1234555s1234m4567p123s5547z")
        self.assertEqual(hand1[tile.Tile(1, 's')], 2)
        self.assertEqual(hand1[tile.Tile(4, 's')], 1)
        self.assertEqual(hand1[tile.Tile(5, 's')], 3)
        self.assertEqual(hand1[tile.Tile(5, 'p')], 1)
