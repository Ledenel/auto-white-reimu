from unittest import TestCase

from mahjong.record.reader import from_url

"""
http://tenhou.net/0/?log=2018110323gm-0009-0000-e81b9df3&tw=1
http://tenhou.net/0/?log=2012060420gm-0009-10011-acfd4b57
4f:http://tenhou.net/0/?log=2019011500gm-00a9-0000-297d5c4d
3f:http://tenhou.net/0/?log=2019011500gm-00b9-0000-3065ca3c

4f-disconnected:http://tenhou.net/0/?log=2019012301gm-00a9-0000-420858f6&tw=0&tdsourcetag=s_pcqq_aiomsg
"""


class TestTenhouRecord(TestCase):
    def test_record_games(self):
        record = from_url("http://tenhou.net/0/?log=2019011500gm-00a9-0000-297d5c4d")
        assert len(record.game_list) == 13
