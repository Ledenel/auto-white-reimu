from unittest import TestCase

from mahjong.record.reader import from_url


class TestTenhouRecord(TestCase):
    def test_record_games(self):
        record = from_url("http://tenhou.net/0/?log=2019011500gm-00a9-0000-297d5c4d")
        assert len(record.game_list) == 13
