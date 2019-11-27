import logging
from xml.etree.ElementTree import Element

from mahjong.record.utils.bit import unpack_with
from mahjong.record.utils.value.general import number_list
from mahjong.record.utils.value.meld import meld_from, MeldTypeData, meld_type_unpacker
from mahjong.record.utils.value.tile import tile_from_tenhou
from .constant import DRAW_ALL_REGEX, DISCARD_ALL_REGEX, DRAW_GROUPED_REGEX, DISCARD_GROUPED_REGEX, DISCARD_INDICATOR, \
    DRAW_INDICATOR, DRAWN_TYPES


def is_game_init(event):
    return event.tag == "INIT"


def is_open_hand(event):
    return event.tag == "N"


def is_dora_indicator_event(event):
    return event.tag == "DORA"


def is_richii(event):
    return event.tag == "REACH"


def is_somebody_win_game(event):
    return event.tag == "AGARI"


def is_nobody_win_game(event):
    return event.tag == "RYUUKYOKU"


def draw_value(event):
    matched = DRAW_ALL_REGEX.match(event.tag)
    if matched:
        return int(matched.group(1))


def discard_value(event):
    matched = DISCARD_ALL_REGEX.match(event.tag)
    if matched:
        return int(matched.group(1))


def tile_change(event, regex, indicator):
    matched = regex.match(event.tag)
    if matched:
        return {
            'tile': tile_from_tenhou(int(matched.group(2))),
            'player': indicator.index(matched.group(1))
        }


def draw_tile_change(event):
    return tile_change(event, DRAW_GROUPED_REGEX, DRAW_INDICATOR)


def discard_tile_change(event):
    return tile_change(event, DISCARD_GROUPED_REGEX, DISCARD_INDICATOR)


class TenhouEvent:
    def __init__(self, xml_element: Element):
        self._wrapped_xml_event = xml_element

    def __getattr__(self, name):
        return getattr(self._wrapped_xml_event, name)

    def __repr__(self):
        return "<%s>" % self

    @property
    def meta_attribute(self):
        return self._wrapped_xml_event.attrib

    def __str__(self):
        event = self._wrapped_xml_event
        attrs = event.attrib
        draw = draw_tile_change(event)
        if draw:
            return "player {player} draw {tile}".format(**draw)
        discard = discard_tile_change(event)
        if discard:
            return "player {player} discard {tile}".format(**discard)
        if is_open_hand(event):
            return "player {who} claimed {item}".format(
                who=attrs['who'],
                item=meld_from(event)
            )
        if is_richii(event):
            return "player {who} richii".format(
                who=attrs['who'],
            )
        if is_dora_indicator_event(event):
            return "new dora indicator {tile}".format(
                tile=tile_from_tenhou(int(attrs['hai'])),
            )
        if is_somebody_win_game(event):
            return 'player {winner} win {score} from player {loser}'.format(
                winner=attrs['who'],
                loser=attrs['fromWho'],
                score=number_list(event.attrib['ten'])[1],
            )
        if is_nobody_win_game(event):
            return 'no body win {reason}'.format(
                reason=DRAWN_TYPES[attrs['type']]
                if 'type' in attrs else '',
            )

        return "UNPARSED {tag}: {attr_expr}".format(
            tag=event.tag,
            attr_expr=",".join("{}={}".format(k, v) for k, v in attrs.items()),
        )

    def to_paifu(self):
        event = self._wrapped_xml_event
        attrs = event.attrib
        if event.tag == 'INIT':
            dict0 = {'event_type': 'INIT1', 'player': '0', 'player_see': ''.join(
                [str(tile_from_tenhou(i)) for i in sorted([int(i) for i in attrs['hai0'].split(',')])]),
                     'score': attrs['ten'].split(',')[0] + '00'}
            dict1 = {'event_type': 'INIT2', 'player': '1', 'player_see': ''.join(
                [str(tile_from_tenhou(i)) for i in sorted([int(i) for i in attrs['hai1'].split(',')])]),
                     'score': attrs['ten'].split(',')[1] + '00'}
            dict2 = {'event_type': 'INIT3', 'player': '2', 'player_see': ''.join(
                [str(tile_from_tenhou(i)) for i in sorted([int(i) for i in attrs['hai2'].split(',')])]),
                     'score': attrs['ten'].split(',')[2] + '00'}
            dora = {'event_type': 'DORA', 'player': '0',
                    'player_see': str(tile_from_tenhou(int(attrs['seed'].split(',')[-1]))),
                    'player_show': str(tile_from_tenhou(int(attrs['seed'].split(',')[-1])))}
            initround = {'event_type': 'ROUND', 'score': attrs['seed'].split(',')[2] + '000'}
            if ('hai3' in attrs.keys()) and (attrs['hai3'] != ''):
                dict3 = {'event_type': 'INIT4', 'player': '3', 'player_see': ''.join(
                    [str(tile_from_tenhou(i)) for i in sorted([int(i) for i in attrs['hai3'].split(',')])]),
                         'score': attrs['ten'].split(',')[3] + '00'}
                return [dict0, dict1, dict2, dict3, dora, initround]
            else:
                return [dict0, dict1, dict2, dora, initround]
        draw = draw_tile_change(event)
        if draw:
            player, tile = draw['player'], draw['tile']
            return [{'event_type': 'DRAW', 'player': str(player), 'player_see': str(tile)}]
        discard = discard_tile_change(event)
        if discard:
            player, tile = discard['player'], discard['tile']
            return [{'event_type': 'DISCARD', 'player': str(player), 'player_show': str(tile)}]
        if is_open_hand(event):

            player = attrs['who']
            item = meld_from(event)
            type_of = unpack_with(MeldTypeData, meld_type_unpacker, event.attrib['m'])
            source = item.from_who
            self_tile = item.self_tiles
            borrow_tile = item.borrowed_tiles
            if type_of.syuntsu:
                return [{'event_type': 'CHI', 'player': str(player),
                         'player_show': ''.join([str(tile_from_tenhou(int(i))) for i in self_tile]),
                         'player_open': ''.join([str(tile_from_tenhou(int(i))) for i in borrow_tile]) + ''.join(
                             [str(tile_from_tenhou(int(i))) for i in self_tile]), 'origin': str(source)}]
            elif type_of.koutsu:
                return [{'event_type': 'PENG ', 'player': str(player),
                         'player_show': ''.join([str(tile_from_tenhou(int(i))) for i in self_tile]),
                         'player_open': ''.join([str(tile_from_tenhou(int(i))) for i in borrow_tile]) + ''.join(
                             [str(tile_from_tenhou(int(i))) for i in self_tile]), 'origin': str(source)}]
            elif type_of.chakan:
                return [{'event_type': 'GANG', 'player': str(player),
                         'player_show': ''.join([str(tile_from_tenhou(int(i))) for i in self_tile]),
                         'player_open': ''.join([str(tile_from_tenhou(int(i))) for i in borrow_tile]) + ''.join(
                             [str(tile_from_tenhou(int(i))) for i in self_tile]), 'origin': str(source)}]
            elif type_of.nuki:
                return [{'event_type': 'KITA', 'player': str(player),
                         'player_show': str([tile_from_tenhou(i) for i in self_tile][0]),
                         'player_open': str([tile_from_tenhou(i) for i in self_tile][0])}]
            else:
                if len(borrow_tile) == 0:
                    return [{'event_type': 'ANGANG', 'player': str(player),
                             'player_show': ''.join([str(tile_from_tenhou(int(i))) for i in self_tile]),
                             'player_open': ''.join([str(tile_from_tenhou(int(i))) for i in self_tile]),
                             'origin': str(source)}]
                else:
                    return [{'event_type': 'MINGGANG', 'player': str(player),
                             'player_show': ''.join([str(tile_from_tenhou(int(i))) for i in self_tile]),
                             'player_open': ''.join([str(tile_from_tenhou(int(i))) for i in borrow_tile]) + ''.join(
                                 [str(tile_from_tenhou(int(i))) for i in self_tile]), 'origin': str(source)}]

        if is_richii(event):
            player = attrs['who']
            status = attrs['step']
            if status == '1':
                return [{'event_type': 'CALLRICHI', 'player': str(player)}]
            if status == '2':
                richi = {'event_type': 'RICHI', 'player': str(player)}
                score = {'event_type': 'SCORE', 'player': str(player), 'score': '-1000'}
                return [richi, score]

        if is_dora_indicator_event(event):
            tile = tile_from_tenhou(int(attrs['hai']))
            return [{'event_type': 'DORA', 'player': '0', 'player_see': tile, 'player_show': tile}]

        if is_somebody_win_game(event):
            player = attrs['who']
            loser = attrs['fromWho']
            score = number_list(event.attrib['ten'])[1]
            return [{'event_type': 'WIN', 'player': str(player), 'origin': str(loser)}]

        if is_nobody_win_game(event):
            return [{'event_type': 'EVEN', 'origin': DRAWN_TYPES[attrs['type']] if 'type' in attrs else ''}]

        logging.warning('Unparsed or not support event: {0}'.format(str(event)))
        return []
