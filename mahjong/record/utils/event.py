from xml.etree.ElementTree import Element

from mahjong.record.utils.value.general import number_list
from mahjong.record.utils.value.meld import meld_from
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
