from __future__ import annotations

import xml.etree.ElementTree as ET
from argparse import Namespace
from functools import reduce
from itertools import groupby
from urllib.parse import urlparse, parse_qs

import requests

from .player import TenhouPlayer
from .utils.constant import API_URL_TEMPLATE
from .utils.value.gametype import GameType
from .utils.event import is_game_init
from .utils.value.general import number_list


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


class TenhouRecord:
    def __init__(self, events):
        self.events = events
        grouped = [(condition, list(group))
                   for condition, group in
                   groupby(events, is_game_init)]
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
        self.game_type = GameType(meta.GO.type)
        player_mode = self.game_type.player_count()
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
