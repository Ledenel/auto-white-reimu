import os
from unittest import TestCase

from mahjong.record.reader import from_file


class TestFromFile(TestCase):
    def test_from_file(self):
        filename = os.path.join("tests", "2009060321gm-00b9-0000-75b25bcf.xml")
        record = from_file(filename)
        assert len(record.game_list) == 1
