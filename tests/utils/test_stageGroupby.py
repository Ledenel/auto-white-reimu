from unittest import TestCase

import pytest

from mahjong.record.stage import StageGroupby

origins = """AAABBB
AAABBBAAACCC
AAABBBCCCABCDEDCBA
ABBBBBCBBBBBBA"""

stages = """A,B
A,C
B,C
A,B,C"""

keys = [
    [["A", "B"]],
    [["A", "C"], "B", ["A", "C"]],
    ["A", ["B", "C"], "A", ["B", "C"], "D", "E", "D", ["C"], ["B", "C"], "A"],
    [["A", "B", "C"], ["B", "C"], ["A", "B", "C"]]
]

values = """AAABBB
AAA BBB AAACCC
AAA BBBCCC A BC D E D C B A
ABBBBBC BBBBBB A"""


@pytest.mark.parametrize("ori,stage,key", zip(
    origins.split('\n'),
    (x.split(",") for x in stages.split('\n')),
    keys
))
def test_stage_group_key(ori, stage, key):
    assert list(k for k, _ in StageGroupby(ori, *stage)) == key


@pytest.mark.parametrize("ori,stage,value", zip(
    origins.split('\n'),
    (x.split(",") for x in stages.split('\n')),
    (list(list(y) for y in x.split(" ")) for x in values.split('\n'))
))
def test_stage_group_key(ori, stage, value):
    assert list(list(g) for _, g in StageGroupby(ori, *stage)) == value
