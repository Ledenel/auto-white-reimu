from unittest import TestCase

from tile import tile_set_from_string, NormalTypeWin


class TestWinPattern(TestCase):
    def test_unique_win_selections(self):
        assert sum(1 for _ in NormalTypeWin().unique_win_selections(
            tile_set_from_string("111123456s55567p")
        )) == 1
