from collections import Iterable
from unittest import TestCase

import pytest

from mahjong.container.utils import tile_set_from_string
from mahjong.container.pattern.win import NormalTypeWin


def counting(iterable: Iterable) -> int:
    return sum(1 for _ in iterable)


class TestWinPattern(TestCase):
    def test_win_selections(self):
        hand = tile_set_from_string("111123456s55567p")
        item = next(NormalTypeWin().win_selections(hand))
        answer = ["111s", "123s", "456s", "55p", "567p"]
        assert sorted(item) == sorted(tile_set_from_string(x) for x in answer)

    def test_not_ordered_win_selections(self):
        hand = tile_set_from_string("11s555p1123456s67p")
        item = next(NormalTypeWin().win_selections(hand))
        answer = ["111s", "123s", "456s", "55p", "567p"]
        assert sorted(item) == sorted(tile_set_from_string(x) for x in answer)

    def test_reversed_win_selections(self):
        hand = tile_set_from_string("654321111s76555p")
        item = next(NormalTypeWin().win_selections(hand))
        answer = ["111s", "123s", "456s", "55p", "567p"]
        assert sorted(item) == sorted(tile_set_from_string(x) for x in answer)

    def test_compare_tile_set(self):
        hand_a = tile_set_from_string("567p")
        hand_b = tile_set_from_string("55p")
        assert (hand_a < hand_b) ^ (hand_a > hand_b)
        assert (hand_b < hand_a) ^ (hand_b > hand_a)

    def test_unique_win_selections(self):
        assert counting(NormalTypeWin().unique_win_selections(
            tile_set_from_string("111123456s55567p")
        )) == 1

    def test_multi_win_selections(self):
        assert counting(NormalTypeWin().unique_win_selections(
            tile_set_from_string("111123456s55567p8p")
        )) == 3


hands = [
    "1112246667778899m",
]

answers = [
    "111m,22m,666m,789m,789m",
]


@pytest.mark.parametrize("hand,ans", zip(hands, answers))
def test_tenhou_reasoning(hand, ans):
    answer = [sorted(tile_set_from_string(x) for x in selection.split(',')) for selection in ans.split(';')]
    answer.sort()
    assert sorted(NormalTypeWin().unique_win_selections(tile_set_from_string(hand))) == answer
