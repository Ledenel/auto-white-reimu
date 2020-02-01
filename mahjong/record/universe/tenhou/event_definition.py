from typing import Union, Iterable

from loguru import logger

from mahjong.record.player import TenhouPlayer
from mahjong.record.reader import TenhouGame
from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.format import PlayerView, Update, GameView, RecordView, PlayerId
from mahjong.record.universe.tenhou.xml_macher import tenhou_command
from mahjong.record.utils.builder import Builder
from mahjong.record.utils.event import *
from mahjong.record.utils.value.gametype import GameType, if_value
from mahjong.record.utils.value.meld import Kita


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
def draw_command(event: TenhouEvent, ctx):
    draw = draw_tile_tenhou(event)
    if draw:
        yield GameCommand(
            prop=PlayerView.hand,
            update=Update.ADD,
            sub_scope=draw['player'],
            value=tile_str_list([draw['tile']])
        )


@tenhou_command.default_event
def discard_command(event: TenhouEvent, ctx):
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
def game_init_command(event: TenhouEvent, ctx):
    _not_fully_support(event)
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
                    yield cmd(prop=PlayerView.bonus_tiles)
                yield cmd(prop=PlayerView.in_richii, value=False)
                yield cmd(prop=PlayerView.hand, value=tile_str_list(event.attrib['hai{}'.format(player_id)]))
                with cmd.when(update=Update.ASSERT_EQUAL_OR_SET):
                    yield cmd(prop=PlayerView.score, value=score_all[player_id] * 100)


def _not_fully_support(event):
    logger.warning("event {} not fully parsed.", event)


@tenhou_command.match_name("N")
def open_hand(event: TenhouEvent, ctx):
    meld = meld_from(event)
    cmd = Builder(GameCommand)
    with cmd.when(sub_scope=int(event.attrib["who"])):
        with cmd.when(update=Update.ADD):
            yield cmd(prop=PlayerView.meld_public_tiles, value=tile_str_list(meld.self_tiles))
            meld_value = tile_str_list(meld.self_tiles | meld.borrowed_tiles)
            if not isinstance(meld, Kita):
                yield cmd(prop=PlayerView.fixed_meld, value=[meld_value])
            else:
                yield cmd(prop=PlayerView.bonus_tiles, value=meld_value)
        with cmd.when(update=Update.REMOVE):
            yield cmd(prop=PlayerView.hand, value=tile_str_list(meld.self_tiles))


@tenhou_command.match_name("GO")
def game_type_command(event: TenhouEvent, ctx):
    cmd = Builder(GameCommand)
    game_type = GameType(event.attrib["type"])
    with cmd.when(update=Update.REPLACE):
        yield cmd(
            prop=RecordView.play_level,
            value=if_value(game_type.with_tips(), "若銀琥孔", "般上特鳳")[game_type.play_level()]
        )
        yield cmd(prop=RecordView.show_discard_shadow, value=game_type.show_discard_shadow())
        yield cmd(prop=RecordView.play_wind_count, value=game_type.play_wind_count())
        yield cmd(prop=RecordView.allow_tanyao_open, value=game_type.allow_tanyao_open())
        yield cmd(prop=RecordView.speed_up, value=game_type.speed_up())
        yield cmd(prop=RecordView.player_count, value=game_type.player_count())


@tenhou_command.match_name("TAIKYOKU")
def set_oya_command(event: TenhouEvent, ctx):
    yield GameCommand(prop=GameView.oya, value=int(event.attrib['oya']), update=Update.REPLACE)


@tenhou_command.match_name("UN")
def set_player_command(event: TenhouEvent, ctx):
    dan = number_list(event.attrib['dan'])
    rate = number_list(event.attrib['rate'])
    sex = event.attrib['sx'].split(",")
    cmd = Builder(GameCommand)
    for i in PlayerId:
        player_id = i.value
        name_attr = "n%s" % player_id
        if name_attr in event.attrib and event.attrib[name_attr].strip() != "":
            player = TenhouPlayer(
                player_id,
                event.attrib[name_attr],
                dan[player_id],
                rate[player_id],
                sex[player_id]
            )
            with cmd.when(sub_scope=player_id, update=Update.REPLACE):
                yield cmd(prop=PlayerView.name, value=player.name)
                yield cmd(prop=PlayerView.level, value=player.level_str())
                yield cmd(prop=PlayerView.extra_level, value=player.rate)


@tenhou_command.match_name("DORA")
def dora_command(event: TenhouEvent, ctx):
    yield GameCommand(
        prop=GameView.dora_indicators,
        update=Update.ADD,
        value=tile_str_list(event.attrib["hai"])
    )


@tenhou_command.match_name("REACH")
def richii_command(event: TenhouEvent, ctx):
    player_id = int(event.attrib["who"])
    cmd = Builder(GameCommand)
    with cmd.when(sub_scope=player_id):
        if event.attrib["step"] == "1":
            yield cmd(update=Update.REPLACE, prop=PlayerView.in_richii, value=True)
        elif event.attrib["step"] == "2":
            yield cmd(update=Update.REMOVE, prop=PlayerView.score, value=1000)


@tenhou_command.match_name("AGARI")
def agari_command(event: TenhouEvent, ctx):
    game: TenhouGame = event.context_
    _not_fully_support(event)
    player_id = int(event.attrib["who"])
    from_player_id = int(event.attrib["fromWho"])
    sc_list = number_list(event.attrib["sc"])
    sc_score_list = sc_list[::2]
    sc_delta_list = sc_list[1::2]
    cmd = Builder(GameCommand)
    with cmd.when(update=Update.ASSERT_EQUAL_OR_SET, sub_scope=player_id):
        expected_hand = tile_str_list(event.attrib["hai"])
        if player_id != from_player_id:
            expected_hand.remove(tile_str_list(event.attrib["machi"])[0])
        yield cmd(prop=PlayerView.hand, value=expected_hand)
    with cmd.when(update=Update.ADD):
        for p_id in range(len(game.players)):
            with cmd.when(sub_scope=p_id):
                with cmd.when(update=Update.ASSERT_EQUAL_OR_SET):
                    yield cmd(prop=PlayerView.score, value=sc_score_list[p_id] * 100)
                yield cmd(prop=PlayerView.score, value=sc_delta_list[p_id] * 100)


@tenhou_command.match_name("SHUFFLE")
def shuffle_command(event: TenhouEvent, ctx):
    yield GameCommand(
        prop=RecordView.seed,
        value=event.attrib["seed"],
        update=Update.REPLACE,
    )
