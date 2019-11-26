from unittest import TestCase

from mahjong.record.reader import from_file


class TestTile(TestCase):
    def test_tile_from_tenhou(self):
        a = from_file("tests/2009060321gm-00b9-0000-75b25bcf.xml")
        retlen = []
        for z in a.game_list:
            for i in z.events:
                ret = i.to_paifu()
                retlen.append(len(ret))
        assert retlen == [5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                          1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
