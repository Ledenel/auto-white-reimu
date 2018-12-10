from unittest import TestCase

from tile import tile_set_from_string, NormalTypeWin


class TestWinPattern(TestCase):
    def test_win_selections(self):
        hand = tile_set_from_string("111123456s55567p")
        print(hand)
        for select in NormalTypeWin().win_selections(hand):
            print(sorted(select))

    def test_not_ordered_win_selections(self):
        hand = tile_set_from_string("11s555p1123456s67p")
        print(hand)
        for select in (NormalTypeWin().win_selections(hand)):
            print(sorted(select))

    def test_reversed_win_selections(self):
        hand = tile_set_from_string("654321111s76555p")
        print(hand)
        for select in NormalTypeWin().win_selections(hand):
            print(sorted(select))

    def test_compare_tile_set(self):
        hand_a = tile_set_from_string("567p")
        hand_b = tile_set_from_string("55p")
        assert (hand_a < hand_b) ^ (hand_a > hand_b)
        assert (hand_b < hand_a) ^ (hand_b > hand_a)
