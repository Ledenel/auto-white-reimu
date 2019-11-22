from unittest import TestCase

from mahjong.record.reader import from_file


class TestFromFile(TestCase):
    def test_from_file(self):
        filename = "2009060321gm-00b9-0000-75b25bcf.xml"
        record = from_file(filename)
        assert str(record) == '三鳳南喰赤 1位:トバゾ(66.0),2位:神速★.com(-5.0),3位:一歩(-61.0)'
