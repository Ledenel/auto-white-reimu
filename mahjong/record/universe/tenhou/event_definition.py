import math
from typing import Union, Iterable

from loguru import logger

from mahjong.record.const import initial_tiles
from mahjong.record.category import SubCategory
from mahjong.record.player import TenhouPlayer
from mahjong.record.reader import TenhouGame
from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.format import PlayerView, Update, GameView, RecordView, PlayerId, EventType
from mahjong.record.universe.tenhou.xml_macher import tenhou_command
from mahjong.record.universe.translator import default_event_type
from mahjong.record.utils.builder import Builder
from mahjong.record.utils.constant import SCORE_PATTERN
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
@default_event_type(EventType.draw)
def draw_command(event: TenhouEvent, ctx):
    draw = draw_tile_tenhou(event)
    if draw:
        cmd = Builder(GameCommand)
        with cmd.when(update=Update.ADD, sub_scope=draw['player']):
            yield from hand_update(cmd, [draw['tile']], ctx)


@tenhou_command.default_event
@default_event_type(EventType.discard)
def discard_command(event: TenhouEvent, ctx):
    discard = discard_tile_tenhou(event)
    cmd = Builder(GameCommand)
    if discard:
        tile_raw = discard['tile']
        player_id = discard['player']
        with cmd.when(
                sub_scope=player_id,
                value=tile_str_list([tile_raw]),
        ):
            yield cmd(prop=PlayerView.round, update=Update.ADD, value=1)
            discard = int(tile_raw)
            draw_tile = ctx[(player_id, "_right_most_tile_int")]
            yield cmd(prop=PlayerView.discard_from_hand, update=Update.ADD,
                      value=[discard != draw_tile])
            with cmd.when(update=Update.REMOVE):
                yield from hand_update(cmd, str(tile_raw), ctx)
            yield cmd(prop=PlayerView.discard_tiles, update=Update.ADD)


@tenhou_command.match_name("INIT")
@default_event_type(EventType.game_init)
def game_init_command(event: TenhouEvent, ctx):
    _not_fully_support(event)
    seed = number_list(event.attrib["seed"])
    game_indexer = ctx["_game_indexer"]
    sub_game = seed[1]
    richii_counts = seed[2]
    initial_dora = seed[-1]
    cmd = Builder(GameCommand)
    with cmd.when(update=Update.REPLACE):
        prevailing, game_index = game_indexer.category(seed[0])
        yield cmd(prop=GameView.wind, value=prevailing)
        yield cmd(prop=GameView.round, value=game_index)
        yield cmd(prop=GameView.sub_round, value=sub_game)
        yield cmd(prop=GameView.richii_remain_scores, value=richii_counts * 1000)
        oya_index = int(event.attrib["oya"])
        yield from set_oya_command_yield(cmd, ctx, oya_index)
        yield cmd(prop=GameView.dora_indicators, value=tile_str_list([initial_dora]), event=EventType.new_dora)
        for player_id in range(ctx[("all", RecordView.player_count)]):
            score_all = number_list(event.attrib['ten'])
            with cmd.when(sub_scope=player_id):
                with cmd.when(update=Update.RESET_DEFAULT):
                    yield cmd(prop=PlayerView.discard_tiles)
                    yield cmd(prop=PlayerView.fixed_meld)
                    yield cmd(prop=PlayerView.meld_public_tiles)
                    yield cmd(prop=PlayerView.bonus_tiles)
                    yield cmd(prop=PlayerView.round)
                yield cmd(prop=PlayerView.in_richii, value=False)
                hand_raw = event.attrib['hai{}'.format(player_id)]
                yield from hand_update(cmd, hand_raw, ctx)
                with cmd.when(update=Update.ASSERT_EQUAL_OR_SET):
                    yield cmd(prop=PlayerView.score, value=score_all[player_id] * 100)


def set_oya_command_yield(cmd, ctx, oya_index):
    with cmd.when(update=Update.REPLACE):
        for p_id in range(ctx[("all", RecordView.player_count)]):
            yield cmd(prop=PlayerView.is_dealer, sub_scope=p_id, value=oya_index == p_id)


def hand_update(cmd: Builder, hand_raw, ctx):
    update_method = cmd.inner_state.merged_dict["update"]
    player_id = cmd.inner_state.merged_dict["sub_scope"]
    update_method: Update
    key = (player_id, "_right_most_tile_int")
    new_tile = ctx.get(key, None)
    if isinstance(hand_raw, str):
        hand_raw = number_list(hand_raw)
    if update_method == Update.ADD:
        assert len(hand_raw) == 1, "Player can only draw one tile."
        new_tile = hand_raw[0]
    elif update_method == Update.REMOVE:
        new_tile = None
    elif update_method == Update.REPLACE:
        yield cmd(update=Update.RESET_DEFAULT, prop=PlayerView.discard_from_hand)
        new_tile = None
    ctx[key] = new_tile
    yield cmd(prop=PlayerView.hand, value=tile_str_list(hand_raw))


def _not_fully_support(event):
    logger.warning("event {} not fully parsed.", event)


@tenhou_command.match_name("N")
@default_event_type(EventType.open_hand)
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
            yield from hand_update(cmd, meld.self_tiles, ctx)


@tenhou_command.match_name("GO")
@default_event_type(EventType.record_init)
def game_type_command(event: TenhouEvent, ctx):
    cmd = Builder(GameCommand)
    game_type = GameType(event.attrib["type"])
    ctx["_game_indexer"] = SubCategory(
        game_type.play_wind_count() + 1, 4, caption="prevailing_and_game",
        names=["prevailing", "game_index"]
    )
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
        yield cmd(prop=RecordView.using_tiles, value=initial_tiles(game_type.player_count(), game_type.has_aka_dora()))

@tenhou_command.match_name("TAIKYOKU")
@default_event_type(EventType.game_init)
def set_oya_command(event: TenhouEvent, ctx):
    yield from set_oya_command_yield(Builder(GameCommand), ctx, int(event.attrib['oya']))


@tenhou_command.match_name("UN")
@default_event_type(EventType.record_init)
def set_player_command(event: TenhouEvent, ctx):
    dan = number_list(get_list_attr("dan", event))
    rate = number_list(get_list_attr("rate", event))
    sex = get_list_attr("sx", event).split(",")
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
                yield cmd(prop=PlayerView.disconnected, value=False, event=EventType.connect_change)
                yield cmd(prop=PlayerView.name, value=player.name, update=Update.ASSERT_EQUAL_OR_SET)
                if "dan" in event.attrib:
                    yield cmd(prop=PlayerView.level, value=player.level_str())
                if "rate" in event.attrib:
                    yield cmd(prop=PlayerView.extra_level, value=player.rate)


def get_list_attr(attr_name, event):
    if attr_name in event.attrib:
        return event.attrib[attr_name]
    else:
        return ",".join(["-127"] * 4)


@tenhou_command.match_name("DORA")
@default_event_type(EventType.new_dora)
def dora_command(event: TenhouEvent, ctx):
    yield GameCommand(
        prop=GameView.dora_indicators,
        update=Update.ADD,
        value=tile_str_list(event.attrib["hai"])
    )


@tenhou_command.match_name("REACH")
@default_event_type(EventType.richii)
def richii_command(event: TenhouEvent, ctx):
    player_id = int(event.attrib["who"])
    cmd = Builder(GameCommand)
    with cmd.when(sub_scope=player_id):
        if event.attrib["step"] == "1":
            yield cmd(update=Update.REPLACE, prop=PlayerView.in_richii, value=True)
        elif event.attrib["step"] == "2":
            yield cmd(update=Update.REMOVE, prop=PlayerView.score, value=1000)


@tenhou_command.match_name("AGARI")
@default_event_type(EventType.game_finish)
def agari_command(event: TenhouEvent, ctx):
    _not_fully_support(event)
    player_id = int(event.attrib["who"])
    from_player_id = int(event.attrib["fromWho"])
    sc_list = number_list(event.attrib["sc"])
    cmd = Builder(GameCommand)
    with cmd.when(update=Update.ASSERT_EQUAL_OR_SET, sub_scope=player_id):
        expected_hand = tile_str_list(event.attrib["hai"])
        if player_id != from_player_id:
            expected_hand.remove(tile_str_list(event.attrib["machi"])[0])
        yield cmd(prop=PlayerView.hand, value=expected_hand)
    with cmd.when(update=Update.REPLACE):
        yield cmd(prop=GameView.nobody_win, value=False)
    attr = event.attrib
    yaku = list(map(lambda t: SCORE_PATTERN[t], number_list(attr.get("yaku", attr.get("yakuman")))))
    yield from game_finish(cmd, ctx, from_player_id, player_id, sc_list, yaku, event)


def game_finish(cmd, ctx, from_player_id, player_id, sc_list, yaku, event):
    player_count_ = ctx[("all", RecordView.player_count)]
    for p_id in range(player_count_):
        with cmd.when(sub_scope=p_id):
            if sc_list is not None:
                sc_score_list = sc_list[::2]
                sc_delta_list = sc_list[1::2]
                with cmd.when(update=Update.ADD):
                    with cmd.when(update=Update.ASSERT_EQUAL_OR_SET):
                        yield cmd(prop=PlayerView.score, value=sc_score_list[p_id] * 100)
                    yield cmd(prop=PlayerView.score, value=sc_delta_list[p_id] * 100)
            with cmd.when(update=Update.REPLACE):
                win = player_id == p_id
                yield cmd(prop=PlayerView.is_win, value=win)
                self_win = player_id == from_player_id
                yield cmd(prop=PlayerView.is_self_win, value=self_win)
                discard_lose = not self_win and p_id == from_player_id
                yield cmd(prop=PlayerView.is_discard_lose_game,
                          value=discard_lose)
                participated = self_win or discard_lose or win
                yield cmd(prop=PlayerView.faans, value=yaku if participated else [])
    if "owari" in event.attrib:
        finals = number_list(event.attrib["owari"])
        final_scores = [x * 100 for x in finals[::2]]
        final_points = finals[1::2]
        player_ranks = [(-score, pid) for pid, score in enumerate(final_scores[:player_count_])]
        player_ranks.sort()
        player_rank_map = {pid: rank+1 for rank, (_, pid) in enumerate(player_ranks)}
        for p_id in range(player_count_):
            with cmd.when(sub_scope=p_id, update=Update.REPLACE, event=EventType.record_finish):
                yield cmd(prop=PlayerView.final_score, value=final_scores[p_id])
                yield cmd(prop=PlayerView.final_point, value=final_points[p_id])
                yield cmd(prop=PlayerView.rank, value=player_rank_map[p_id])


@tenhou_command.match_name("SHUFFLE")
@default_event_type(EventType.record_init)
def shuffle_command(event: TenhouEvent, ctx):
    yield GameCommand(
        prop=RecordView.seed,
        value=event.attrib["seed"],
        update=Update.REPLACE,
    )


@tenhou_command.match_name("BYE")
@default_event_type(EventType.connect_change)
def disconnected_command(event: TenhouEvent, ctx):
    yield GameCommand(
        prop=PlayerView.disconnected,
        update=Update.REPLACE,
        sub_scope=int(event.attrib["who"]),
        value=True,
    )


@tenhou_command.match_name("RYUUKYOKU")
@default_event_type(EventType.game_finish)
def no_win_command(event: TenhouEvent, ctx):
    cmd = Builder(GameCommand)
    with cmd.when(update=Update.REPLACE):
        yield cmd(prop=GameView.nobody_win, value=True)
        yield cmd(prop=GameView.extra_reason,
                  value=DRAWN_TYPES[event.attrib["type"]] if "type" in event.attrib else "EXHAUSTED")

    sc_list = number_list(event.attrib["sc"]) if "sc" in event.attrib else None
    yield from game_finish(cmd, ctx, math.nan, math.nan, sc_list, [], event)
