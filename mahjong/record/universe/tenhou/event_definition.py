from typing import List, Union

from mahjong.record.universe.format import GameCommand, GameProperty, PlayerView, Update
from mahjong.record.utils.event import *
from mahjong.record.universe.tenhou.xml_macher import tenhou_matcher


def tile_str_list(tile_list: Union[str, List[int]]):
    if isinstance(tile_list, str):
        tile_list = number_list(tile_list)

    return [str(tile_from_tenhou(x)) for x in tile_list]


def tile_change_tenhou(event, regex, indicator):
    matched = regex.match(event.tag)
    if matched:
        return {
            'tile': int(matched.group(2)),
            'player': indicator.index(matched.group(1))
        }


def draw_tile_tenhou(event):
    return tile_change(event, DRAW_GROUPED_REGEX, DRAW_INDICATOR)


def discard_tile_tenhou(event):
    return tile_change(event, DISCARD_GROUPED_REGEX, DISCARD_INDICATOR)


@tenhou_matcher.match_names(DRAW_INDICATOR)
def draw_command(event: TenhouEvent):
    draw = draw_tile_change(event)
    if draw:
        return [GameCommand(
            GameProperty(PlayerView.hand, Update.ADD),
            sub_scope_id=draw['player'],
            value=tile_str_list([draw['tile']])
        )]


@tenhou_matcher.match_names(DISCARD_INDICATOR)
def discard_command(event: TenhouEvent):
    discard = discard_tile_change(event)
    if discard:
        return [GameCommand.multi_command([
            GameProperty(PlayerView.hand, Update.REMOVE),
            GameProperty(PlayerView.discard_tiles, Update.ADD)
        ],
            sub_scope_id=discard['player'],
            value=tile_str_list([discard['tile']])
        )]
