import operator as op
from functools import reduce
from itertools import groupby
from typing import Set, List, Callable, TypeVar, Optional

import jinja2
from jinja2 import Environment, PackageLoader, select_autoescape

from mahjong.container.pattern.reasoning import HeuristicPatternMatchWaiting
from mahjong.container.pattern.win import NormalTypeWin, UniquePairs
from mahjong.container.set import TileSet
from mahjong.record.reader import from_url, log_id_from_url
from mahjong.record.state import PlayerHand, InvisibleTiles, PlayerMeld
from mahjong.record.utils.value.meld import Kita
from mahjong.record.utils.value.tile import tile_from_tenhou, tile_to_tenhou_range
from mahjong.tile.definition import Tile


def n_a_r(n, r):
    return reduce(op.mul, range(n, n - r, -1), 1)


def n_c_r(n, r):
    r = min(r, n - r)
    return n_a_r(n, r) / n_a_r(r, r)


class ReasoningItem:
    def __init__(self, discard_tile: Tile, waiting_step: int, useful_tiles: Set[Tile],
                 useful_tiles_count: int):
        self.discard_tile = discard_tile
        self.waiting_step = waiting_step
        self.useful_tiles = useful_tiles
        self.useful_tiles_count = useful_tiles_count


class RoundReasoning:
    def __init__(self, hand: TileSet, your_choice_reasoning: ReasoningItem,
                 expected_reasonings: List[ReasoningItem]):
        self.hand = hand
        self.your_choice_reasoning = your_choice_reasoning
        self.expected_reasonings = expected_reasonings


class GameAnalysis:
    def __init__(self, name: str, rounds: List[RoundReasoning]):
        self.name = name
        self.rounds = rounds


def reduce_useful(x: ReasoningItem, y: ReasoningItem) -> ReasoningItem:
    if x.waiting_step > y.waiting_step:
        return y
    elif x.waiting_step == y.waiting_step:
        return ReasoningItem(x.discard_tile, x.waiting_step, x.useful_tiles | y.useful_tiles, 0)
    else:
        return x


def reasoning_merge(reason_list: List[ReasoningItem], invisible_set: Set[int]) -> ReasoningItem:
    tiles_reasoning_item = reduce(reduce_useful, reason_list)
    return ReasoningItem(reason_list[0].discard_tile,
                         min(item.waiting_step for item in reason_list), tiles_reasoning_item.useful_tiles,
                         sum(len(set(tile_to_tenhou_range(tile)) | invisible_set)
                             for tile in tiles_reasoning_item.useful_tiles))


def reasoning_key(x: ReasoningItem):
    return x.waiting_step, -x.useful_tiles_count


T = TypeVar("T")


def find_in_list(lst: List[T], key: Callable[[T], bool]) -> Optional[T]:
    return next((x for x in lst if key(x)), None)


def main():
    log_url = input('Input your tenhou.net log link:').strip()
    name = input('Input your tenhou.net display name:').strip('\n')
    record = from_url(log_url)
    player = next((x for x in record.players if x.name == name), None)
    if player is None:
        raise ValueError("Player '%s' not found in record %s." % (name, record))
    env = Environment(
        loader=PackageLoader('yourapplication', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("record_checker_template.html")

    games = [GameAnalysis(str(game), game_reason_list(game, player, record)) for game in record.game_list]

    with open("tenhou_record_%s_%s.html" % (log_id_from_url(log_url), player.name), "w") as result_file:
        result_file.write(template.render(
            player=str(player),
            record=str(record),
            log_url=log_url,
            games=games
        ))


def game_reason_list(game, player, record):
    hand_state = PlayerHand(player)
    player_meld_state = PlayerMeld(player)
    invisible_tiles_state = InvisibleTiles(player, len(record.players))
    return list(game_reasoning(game, hand_state, invisible_tiles_state, player, player_meld_state))


def game_reasoning(game, hand_state, invisible_tiles_state, player, player_meld_state):
    for discarded, g in groupby(game.events, lambda e: player.is_discard(e)):
        round_of_game = list(g)
        discard_event = round_of_game[0]
        if discarded:
            # TODO reasoning
            yield discard_reasoning(discard_event, hand_state, invisible_tiles_state, player, player_meld_state)

        else:
            hand_state = hand_state.with_events(round_of_game)
            invisible_tiles_state = invisible_tiles_state.with_events(round_of_game)
            player_meld_state = player_meld_state.with_events(round_of_game)


def discard_reasoning(discard_event, hand_state, invisible_tiles_state, player, player_meld_state):
    invisible_player_perspective = invisible_tiles_state.value - set(hand_state.value)
    meld_count = sum(1 for meld in player_meld_state.value if not isinstance(meld, Kita))
    hand = TileSet(tile_from_tenhou(index) for index in hand_state.value)
    win_types = [NormalTypeWin(melds=4 - meld_count)]
    reasoning_names = ["normal_reasonings", "seven_pair_reasonings"]
    if meld_count == 0:
        win_types.append(UniquePairs())
    win_reasonings = [
        list(reasoning_discards(hand, invisible_player_perspective, tile, win) for tile in hand)
        for win in win_types
    ]
    merged_win_reasonings = [
        reasoning_merge(list(reasoning_same_discard), invisible_player_perspective)
        for reasoning_same_discard in zip(*win_reasonings)
    ]
    merged_win_reasonings.sort(key=reasoning_key)
    _, expected_reasonings = next(groupby(merged_win_reasonings, key=reasoning_key))
    expected_reasonings = list(expected_reasonings)
    your_choice_tile = tile_from_tenhou(player.discard_tile_index(discard_event))
    your_choice_reasoning = find_in_list(merged_win_reasonings,
                                         key=lambda x: x.discard_tile == your_choice_tile)
    for win_reasoning in win_reasonings:
        win_reasoning.sort(key=reasoning_key)
    round_reasoning = RoundReasoning(hand, your_choice_reasoning, expected_reasonings)
    for name, win_reason in zip(reasoning_names, win_reasonings):
        setattr(round_reasoning, name, win_reason)
    return round_reasoning


def reasoning_discards(hand, invisible_player_perspective, tile, win):
    hand_temp = hand - TileSet([tile])
    reasoning = HeuristicPatternMatchWaiting(win)
    waiting_step, useful_tiles = reasoning.waiting_and_useful_tiles(hand_temp)
    useful_tiles_count = sum(len(set(tile_to_tenhou_range(tile)) | invisible_player_perspective)
                             for tile in useful_tiles)
    return ReasoningItem(tile, waiting_step, useful_tiles, useful_tiles_count)


if __name__ == '__main__':
    main()
