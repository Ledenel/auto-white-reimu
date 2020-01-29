from typing import Union, Iterable

from mahjong.record.reader import TenhouGame
from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.format import PlayerView, Update, GameView
from mahjong.record.universe.tenhou.xml_macher import tenhou_command
from mahjong.record.utils.builder import Builder
from mahjong.record.utils.event import *


def tile_str_list(tile_list: Union[str, Iterable[int]]):
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
    return tile_change_tenhou(event, DRAW_GROUPED_REGEX, DRAW_INDICATOR)


def discard_tile_tenhou(event):
    return tile_change_tenhou(event, DISCARD_GROUPED_REGEX, DISCARD_INDICATOR)


@tenhou_command.default_event
def draw_command(event: TenhouEvent):
    draw = draw_tile_tenhou(event)
    if draw:
        yield GameCommand(
            prop=PlayerView.hand,
            update=Update.ADD,
            sub_scope=draw['player'],
            value=tile_str_list([draw['tile']])
        )


@tenhou_command.default_event
def discard_command(event: TenhouEvent):
    discard = discard_tile_tenhou(event)
    cmd = Builder(GameCommand)
    if discard:
        with cmd.when(
                sub_scope=discard['player'],
                value=tile_str_list([discard['tile']]),
        ):
            yield cmd(prop=PlayerView.hand, update=Update.REMOVE)
            yield cmd(prop=PlayerView.discard_tiles, update=Update.ADD)


@tenhou_command.match_name("INIT")
def game_init_command(event: TenhouEvent):
    game_context: TenhouGame = event.context_
    cmd = Builder(GameCommand)
    with cmd.when(update=Update.REPLACE):
        prevailing, game_index = game_context.game_index()
        yield cmd(prop=GameView.wind, value=prevailing)
        yield cmd(prop=GameView.round, value=game_index)
        yield cmd(prop=GameView.sub_round, value=game_context.sub_game_index())
        yield cmd(prop=GameView.richii_remain_scores, value=game_context.richii_counts() * 1000)
        yield cmd(prop=GameView.oya, value=game_context.east_index)
        yield cmd(prop=GameView.dora_indicators, value=tile_str_list([game_context.initial_dora()]))
        for player_id in range(game_context.game_type.player_count()):
            score_all = number_list(event.attrib['ten'])
            with cmd.when(sub_scope=player_id):
                with cmd.when(update=Update.RESET_DEFAULT):
                    yield cmd(prop=PlayerView.discard_tiles)
                    yield cmd(prop=PlayerView.fixed_meld)
                    yield cmd(prop=PlayerView.meld_public_tiles)
                yield cmd(prop=PlayerView.hand, value=tile_str_list(event.attrib['hai{}'.format(player_id)]))
                yield cmd(prop=PlayerView.score, value=score_all[player_id] * 100)


@tenhou_command.match_name("N")
def open_hand(event: TenhouEvent):
    meld = meld_from(event)
    cmd = Builder(GameCommand)
    with cmd.when(sub_scope=int(event.attrib["who"])):
        with cmd.when(update=Update.ADD):
            yield cmd(prop=PlayerView.meld_public_tiles, value=tile_str_list(meld.self_tiles))
            yield cmd(prop=PlayerView.fixed_meld, value=[tile_str_list(meld.self_tiles | meld.borrowed_tiles)])
        with cmd.when(update=Update.REMOVE):
            yield cmd(prop=PlayerView.hand, value=tile_str_list(meld.self_tiles))
