from unittest import TestCase

import pandas as pd

from mahjong.record.reader import from_file


class TestTile(TestCase):
    def test_to_paifu(self):
        a = from_file("tests/2009060321gm-00b9-0000-75b25bcf.xml")
        retlen = 0
        for z in a.game_list:
            for i in z.events:
                ret = i.to_paifu()
                retlen += len(ret)
        assert retlen == 50

    def test_init_to_paifu_sanma(self):
        a = from_file("tests/2009060321gm-00b9-0000-75b25bcf.xml")
        assert len(a.game_list[0].events[0].to_paifu()) == 5

    def test_init_to_paifu_sima(self):
        a = from_file("tests/2009100718gm-00e1-0000-470654d3.xml")
        assert len(a.game_list[0].events[0].to_paifu()) == 6

    def test_pd(self):
        a = from_file("tests/2009060321gm-00b9-0000-75b25bcf.xml")
        pd_frame = pd.DataFrame(a.to_paifu())
        assert len(pd_frame) == 53

        a = from_file("tests/2009100718gm-00e1-0000-470654d3.xml")
        pd_frame = pd.DataFrame(a.to_paifu())
        assert len(pd_frame) == 75

    def test_fin_game(self):
        a = from_file("tests/2009060321gm-00b9-0000-75b25bcf.xml")
        tr = len(a.to_paifu())
        tg = 0
        for i in a.game_list:
            tg += len(i.to_paifu())
        assert tr - tg == 3

        a = from_file("tests/2009100718gm-00e1-0000-470654d3.xml")
        tr = len(a.to_paifu())
        tg = 0
        for i in a.game_list:
            tg += len(i.to_paifu())
        assert tr - tg == 4
