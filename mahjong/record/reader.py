from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from argparse import Namespace
from functools import reduce
from itertools import groupby
from urllib.parse import urlparse, parse_qs, unquote

import requests

from .category import TENHOU_TILE_CATEGORY
from ..tile.definition import Tile
from .util import meld_from

API_URL_TEMPLATE = 'http://e.mjv.jp/0/log/?{0}'


def fetch_record_content(url):
    url = download_url(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/71.0.3578.98 Safari/537.36'}
    return requests.get(url, timeout=3, headers=headers, allow_redirects=True).text


def download_url(view_url):
    log_id = log_id_from_url(view_url)
    view_url = API_URL_TEMPLATE.format(log_id)
    return view_url


def log_id_from_url(view_url):
    log_id = parse_qs(urlparse(view_url).query)['log'][0]
    return log_id


SUIT_ORDER = 'mpsz'

"""
tenhou index is numbered as [1m,1m,1m,1m,2m,2m,...,9m,1p,...,9p,1s,...,9s,1z,...,7z,7z,7z,7z]
numbered first 5m,5s,5p is considered as aka dora.
"""


def tile_from_tenhou(index):
    color, number, _ = TENHOU_TILE_CATEGORY.category(index)
    return Tile(number + 1, SUIT_ORDER[color])


def number_list(int_string: str, split=','):
    return [int(float(x))
            if int(float(x)) == float(x)
            else float(x)
            for x in int_string.split(split)]


class TenhouPlayer:
    def __init__(self, index, name_encoded, level, rate, sex):
        self.sex = sex

        self.rate = rate
        self.level = level
        self.name = unquote(name_encoded)
        self.index = index

    def clear(self):
        pass

    def is_draw(self, event):
        regex = DRAW_REGEX[self.index]
        return regex.match(event.tag)

    def draw_tile_index(self, draw_event):
        regex = DRAW_REGEX[self.index]
        return int(regex.match(draw_event.tag).group(1))

    def is_discard(self, event):
        regex = DISCARD_REGEX[self.index]
        return regex.match(event.tag)

    def discard_tile_index(self, discard_event):
        regex = DISCARD_REGEX[self.index]
        return int(regex.match(discard_event.tag).group(1))

    def is_open_hand(self, event):
        return event.tag == "N" and int(event.attrib["who"]) == self.index

    def opened_hand_type(self, event):
        return meld_from(event)

    def is_reach(self):
        return event.tag == "REACH" and int(event)

    def win(self, from_player, tile_index):
        pass

    def chi(self, from_player, tile_index):
        pass

    def pon(self, from_player, tile_index):
        pass

    def kan(self, from_player, tile_index):
        pass

    def adding_kan(self, tile_index):
        pass


class TenhouGame:
    def __init__(self, game_events):
        init, *playing = game_events
        self._meta = list_of_xml_configs([init])
        self._end_meta = list_of_xml_configs([game_events[-1]])
        self.events = game_events
        self.playing = playing


"""
http://tenhou.net/0/?log=2018110323gm-0009-0000-e81b9df3&tw=1
http://tenhou.net/0/?log=2012060420gm-0009-10011-acfd4b57
4f:http://tenhou.net/0/?log=2019011500gm-00a9-0000-297d5c4d
3f:http://tenhou.net/0/?log=2019011500gm-00b9-0000-3065ca3c

4f-disconnected:http://tenhou.net/0/?log=2019012301gm-00a9-0000-420858f6&tw=0&tdsourcetag=s_pcqq_aiomsg
"""


def xml_message_config_scan(namespace: Namespace, message):
    setattr(namespace, message.tag, Namespace(**message.attrib))
    return namespace


def list_of_xml_configs(xml_element_list):
    return reduce(xml_message_config_scan, xml_element_list, Namespace())


RANKS = [
    '新人',
    '9級',
    '8級',
    '7級',
    '6級',
    '5級',
    '4級',
    '3級',
    '2級',
    '1級',
    '初段',
    '二段',
    '三段',
    '四段',
    '五段',
    '六段',
    '七段',
    '八段',
    '九段',
    '十段',
    '天鳳位'
]

SCORE_PATTERN = [
    # // 一飜
    "門前清自摸和",
    "立直",
    "一発",
    "槍槓",
    "嶺上開花",
    "海底摸月",
    "河底撈魚",
    "平和",
    "断幺九",
    "一盃口",
    "自風 東",
    "自風 南",
    "自風 西",
    "自風 北",
    "場風 東",
    "場風 南",
    "場風 西",
    "場風 北",
    "役牌 白",
    "役牌 發",
    "役牌 中",

    # // 二飜
    "両立直",
    "七対子",
    "混全帯幺九",
    "一気通貫",
    "三色同順",
    "三色同刻",
    "三槓子",
    "対々和",
    "三暗刻",
    "小三元",
    "混老頭",

    # //  三飜
    "二盃口",
    "純全帯幺九",
    "混一色",

    # //  六飜
    "清一色",

    # //  満貫
    "人和",

    # //  役満
    "天和",
    "地和",
    "大三元",
    "四暗刻",
    "四暗刻単騎",
    "字一色",
    "緑一色",
    "清老頭",
    "九蓮宝燈",
    "純正九蓮宝燈",
    "国士無双",
    "国士無双１３面",
    "大四喜",
    "小四喜",
    "四槓子",

    "ドラ",
    "裏ドラ",
    "赤ドラ",
]

DRAW_INDICATOR = ['T', 'U', 'V', 'W']
DISCARD_INDICATOR = ['D', 'E', 'F', 'G']

DRAW_REGEX = [re.compile(r"^%s([0-9]+)" % draw) for draw in DRAW_INDICATOR]
DISCARD_REGEX = [re.compile(r"^%s([0-9]+)" % draw) for draw in DISCARD_INDICATOR]


class TenhouRecord:
    def __init__(self, events):
        player_mode = 4

        self.events = events
        grouped = [(condition, list(group))
                   for condition, group in
                   groupby(events, lambda x: x.tag == "INIT")]
        head, *tail = grouped
        _, head_events = head
        self._meta = list_of_xml_configs(head_events)
        self._end_meta = list_of_xml_configs([events[-1]])
        game_chunks = (tail[i:i + 2] for i in range(0, len(tail), 2))
        self.game_list = []
        for game_chunk in game_chunks:
            initial = []
            for _, group in game_chunk:
                initial += list(group)
            self.game_list.append(TenhouGame(initial))

        meta = self._meta

        self.players = [
            TenhouPlayer(index, name_encoded, level, rate, sex)
            for index, name_encoded, level, rate, sex in zip(
                range(player_mode),
                [meta.UN.n0, meta.UN.n1, meta.UN.n2, meta.UN.n3],
                number_list(meta.UN.dan),
                number_list(meta.UN.rate),
                meta.UN.sx.split(',')
            )
        ]


def from_url(url: str) -> TenhouRecord:
    return TenhouRecord(ET.fromstring(fetch_record_content(url)))


def from_file(file) -> TenhouRecord:
    return TenhouRecord(ET.parse(file))
