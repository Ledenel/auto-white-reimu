from __future__ import annotations

import xml.etree.ElementTree as ET
from argparse import Namespace
from functools import reduce
from typing import List
from urllib.parse import urlparse, parse_qs

import requests

from mahjong.record.category import SubCategory
from .player import TenhouPlayer
from .stage import StageGroupby
from .utils.constant import API_URL_TEMPLATE, DRAWN_TYPES
from .utils.event import is_game_init, is_nobody_win_game, is_somebody_win_game, TenhouEvent
from .utils.value.gametype import GameType
from .utils.value.general import number_list


def fetch_record_content(url, timeout=3):
    url = download_url(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/71.0.3578.98 Safari/537.36'}
    return requests.get(url, timeout=timeout, headers=headers, allow_redirects=True).text


def download_url(view_url):
    log_id = log_id_from_url(view_url)
    view_url = API_URL_TEMPLATE.format(log_id)
    return view_url


def log_id_from_url(view_url):
    log_id = parse_qs(urlparse(view_url).query)['log'][0]
    return log_id


def log_id_to_url(log_id):
    return "http://tenhou.net/0/?log={}".format(log_id)


def is_game_end(event):
    return is_somebody_win_game(event) or is_nobody_win_game(event)


class TenhouGame:
    def __init__(self, game_events, game_type: GameType, players: List[TenhouPlayer]):
        self.players = players
        init, *playing = game_events
        playing = list(playing)
        first_end_index = next(i for (i, x) in enumerate(playing) if is_game_end(x))
        end = [x for x in playing[first_end_index:] if is_game_end(x)]
        self.end_events = end
        self._meta = list_of_xml_configs([init])
        self._end_meta = list_of_xml_configs([game_events[-1]])
        self.events = game_events
        self.playing = playing
        self.game_type = game_type
        self.seeds = number_list(self._meta.INIT.seed)
        self.east_index = int(self._meta.INIT.oya)
        self.prevailing_and_game = SubCategory(
            self.game_type.play_wind_count() + 1, 4, caption="prevailing_and_game",
            names=["prevailing", "game_index"]
        )

    def game_index(self):
        return self.prevailing_and_game.category(self.seeds[0])

    def sub_game_index(self):
        return self.seeds[1]

    def richii_counts(self):
        return self.seeds[2]

    def end_stringify(self, event):
        if is_somebody_win_game(event):
            who, from_who = (int(event.attrib[s]) for s in ['who', 'fromWho'])
            score = number_list(event.attrib['ten'])[1]
            if who == from_who:
                return r"%s:ツモ(%d)" % (
                    self.players[who].name,
                    score
                )
            else:
                return "%s<-%s:ロン(%d)" % (
                    self.players[who].name,
                    self.players[from_who].name,
                    score
                )
        elif is_nobody_win_game(event):
            type_of_draw = ""
            if "type" in event.attrib:
                type_of_draw = DRAWN_TYPES[event.attrib["type"]]
            return " ".join([r"流局", type_of_draw])

    def __str__(self):
        prevailing, game_index = self.game_index()
        return "%s%d局%d本 %s" % (
            "東南西北"[prevailing],
            game_index + 1,
            self.sub_game_index(),
            ",".join(self.end_stringify(e) for e in self.end_events)
        )

    def __repr__(self):
        return "<%s>" % self

    def to_paifu(self):
        paifu_data = []
        prevailing, game_index = self.game_index()
        game_str = "{0}-{1}-{2}".format("ESWN"[prevailing], game_index + 1, self.sub_game_index())
        for i in self.events:
            paifu_data.extend(i.to_paifu())
        for i in paifu_data:
            i['game_str'] = game_str
        return paifu_data


def xml_message_config_scan(namespace: Namespace, message):
    setattr(namespace, message.tag, Namespace(**message.attrib))
    return namespace


def list_of_xml_configs(xml_element_list):
    return reduce(xml_message_config_scan, xml_element_list, Namespace())


class TenhouRecord:
    def __init__(self, events):
        events = [TenhouEvent(event) for event in events]
        self.events = events
        head_events, *game_chunks = list(list(g) for _, g in StageGroupby(events, True, False, key=is_game_init))
        self._meta = list_of_xml_configs(head_events)
        end_event = events[-1]
        self._end_meta = list_of_xml_configs([end_event])

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
        self.game_list = [TenhouGame(item, self.game_type, self.players) for item in game_chunks]
        end_infos = number_list(end_event.attrib['owari'])
        steps = 2
        self.end_score, self.end_point = (end_infos[i::steps] for i in range(steps))

    def __str__(self) -> str:
        player_scores = list(zip(self.players, self.end_score, self.end_point))
        player_scores.sort(key=lambda item: item[1], reverse=True)
        return "%s %s" % (
            self.game_type,
            ",".join(
                "%d位:%s(%.1f)" % (
                    i + 1, player.name, end_point
                )
                for i, (player, end_score, end_point) in enumerate(player_scores)
            )
        )

    def __repr__(self):
        return "<%s>" % self

    def to_paifu(self):
        paifu_data = []
        for i in self.game_list:
            paifu_data.extend(i.to_paifu())
        fin1 = {'event_type': 'FIN1', 'player': '0', 'score': str(self.end_score[0] * 100)}
        fin2 = {'event_type': 'FIN2', 'player': '1', 'score': str(self.end_score[1] * 100)}
        fin3 = {'event_type': 'FIN3', 'player': '2', 'score': str(self.end_score[2] * 100)}
        if len(self.players) == 4:
            fin4 = {'event_type': 'FIN4', 'player': '3', 'score': str(self.end_score[3] * 100)}
            paifu_data.extend([fin1, fin2, fin3, fin4])
        else:
            paifu_data.extend([fin1, fin2, fin3])
        return paifu_data


def from_url(url: str, timeout=3) -> TenhouRecord:
    return TenhouRecord(ET.fromstring(fetch_record_content(url, timeout=timeout)))


def from_file(file) -> TenhouRecord:
    return TenhouRecord(next(ET.parse(file).iter()))
