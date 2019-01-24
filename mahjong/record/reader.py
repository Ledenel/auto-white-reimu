from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from abc import abstractmethod, ABCMeta
from argparse import Namespace
from functools import reduce
from itertools import groupby
from urllib.parse import urlparse, parse_qs, unquote

import requests

from record.category import TENHOU_TILE_CATEGORY
from record.util import meld_from
from tile.definition import Tile

API_URL_TEMPLATE = 'http://e.mjv.jp/0/log/?{0}'


def fetch_record_content(url):
    log_id = parse_qs(urlparse(url).query)['log'][0]
    url = API_URL_TEMPLATE.format(log_id)
    return requests.get(url).text


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


class GameState(metaclass=ABCMeta):
    @abstractmethod
    def scan(self, event) -> GameState:
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    @property
    @abstractmethod
    def is_key_event(self):
        pass

    def with_events(self, events):
        initial_state = self
        for event in events:
            initial_state = initial_state.scan(event)
            yield initial_state

    def with_key_events(self, events):
        initial_state = self
        for event in events:
            if self.is_key_event(event):
                initial_state = initial_state.scan(event)
                yield initial_state


class GameStateCollection(GameState):
    @property
    def is_key_event(self):
        return self._composed_key_event_func

    def __init__(self, **states):
        super().__init__()
        self._states = states
        self._name_space_state = Namespace(**states)

        def is_composed_key_event(event):
            return all(st.is_key_event(event) for st in states.values())

        self._composed_key_event_func = is_composed_key_event

    @property
    def value(self):
        return self._name_space_state

    def scan(self, event) -> GameState:
        return GameStateCollection(
            **{k: v.scan(event) for k, v in self._states.items()}
        )


class PlayerHand(GameState):
    @property
    def value(self):
        return self.hand

    def __init__(self, player: TenhouPlayer, hand=None):
        super().__init__()
        if hand is None:
            hand = set()
        self._player = player
        self.hand = hand

        def hand_is_key_event(event):
            return event.tag == "INIT" or player.is_discard(event) or player.is_draw(event) or player.is_open_hand(event)

        self._key_event_func = hand_is_key_event

    def scan(self, event) -> GameState:
        if event.tag == "INIT":
            return PlayerHand(self._player, set(number_list(event.attrib['hai%d' % self._player.index])))
        elif self._player.is_draw(event):
            return PlayerHand(self._player, self.hand | {self._player.draw_tile_index(event)})
        elif self._player.is_discard(event):
            return PlayerHand(self._player, self.hand - {self._player.discard_tile_index(event)})
        elif self._player.is_open_hand(event):
            meld = meld_from(event)
            return PlayerHand(self._player, self.hand - {meld.self_tiles})
        raise ValueError("unexpected event for PlayerHand")

    @property
    def is_key_event(self):
        return self._key_event_func


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

    def reach(self):
        pass

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
    u'新人',
    u'9級',
    u'8級',
    u'7級',
    u'6級',
    u'5級',
    u'4級',
    u'3級',
    u'2級',
    u'1級',
    u'初段',
    u'二段',
    u'三段',
    u'四段',
    u'五段',
    u'六段',
    u'七段',
    u'八段',
    u'九段',
    u'十段',
    u'天鳳位'
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
