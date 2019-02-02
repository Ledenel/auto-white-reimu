from __future__ import annotations

from abc import ABCMeta, abstractmethod
from argparse import Namespace
from functools import reduce
from itertools import product, chain
from typing import List, Iterator, Set

from mahjong.record.utils.constant import TENHOU_TILE_CATEGORY
from .utils.event import is_game_init, is_open_hand, is_dora_indicator_event, discard_value
from .player import TenhouPlayer
from .utils.value.general import number_list
from .utils.value.meld import meld_from, TenhouAddedKan, Meld, Triplet, KanFromTriplet, is_triplet_of_added_kan


class GameState(metaclass=ABCMeta):
    @abstractmethod
    def scan(self, event) -> GameState:
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    def is_key_event(self, event) -> bool:
        return self.scan(event) != self

    def with_events(self, events) -> Iterator[GameState]:
        initial_state = self
        for event in events:
            initial_state = initial_state.scan(event)
            yield initial_state

    def passed_events(self, events) -> GameState:
        return reduce(lambda x, y: y, self.with_key_events(events), self)

    def with_key_events(self, events) -> Iterator[GameState]:
        initial_state = self
        for event in events:
            if self.is_key_event(event):
                initial_state = initial_state.scan(event)
                yield initial_state


class GameStateCollection(GameState):

    def is_key_event(self, event):
        return any(st.is_key_event(event) for st in self._states.values())

    def __init__(self, **states):
        super().__init__()
        self._states = states
        self._name_space_state = Namespace(**states)

    @property
    def value(self):
        return self._name_space_state

    def scan(self, event) -> GameState:
        return GameStateCollection(
            **{k: v.scan(event) for k, v in self._states.items()}
        )


class PlayerHand(GameState):
    @property
    def value(self) -> Set[int]:
        return self.hand

    def __init__(self, player: TenhouPlayer, hand=None):
        super().__init__()
        if hand is None:
            hand = set()
        self._player = player
        self.hand = hand

    def scan(self, event) -> GameState:
        if is_game_init(event):
            return PlayerHand(self._player, set(number_list(event.attrib['hai%d' % self._player.index])))
        elif self._player.is_draw(event):
            return PlayerHand(self._player, self.hand | {self._player.draw_tile_index(event)})
        elif self._player.is_discard(event):
            return PlayerHand(self._player, self.hand - {self._player.discard_tile_index(event)})
        elif self._player.is_open_hand(event):
            meld = meld_from(event)
            return PlayerHand(self._player, self.hand - meld.self_tiles)
        return self


class PlayerMeld(GameState):
    def __init__(self, player: TenhouPlayer, meld_list=None) -> None:
        super().__init__()
        if meld_list is None:
            meld_list = []

        self._meld_list: List[Meld] = meld_list
        self._player = player

    def scan(self, event) -> GameState:
        if self._player.is_open_hand(event):
            meld = meld_from(event)
            if isinstance(meld, TenhouAddedKan):
                return PlayerMeld(self._player,
                                  [(KanFromTriplet(item, meld)
                                    if isinstance(item, Triplet) and is_triplet_of_added_kan(item, meld)
                                    else item)
                                   for item in self._meld_list]
                                  )
            else:
                return PlayerMeld(self._player, self._meld_list + [meld])
        elif is_game_init(event):
            return PlayerMeld(self._player)
        return self

    @property
    def value(self) -> List[Meld]:
        return self._meld_list

    def is_key_event(self, event):
        return self._player.is_open_hand(event) or is_game_init(event)


class DiscardTiles(GameState):
    def scan(self, event) -> GameState:
        if self._player.is_discard(event):
            return DiscardTiles(self._player, self._discard_tiles + [self._player.discard_tile_index(event)])
        elif is_game_init(event):
            return DiscardTiles(self._player)
        return self

    @property
    def value(self) -> List[int]:
        return self._discard_tiles

    def __init__(self, player: TenhouPlayer, discard_tiles=None):
        if discard_tiles is None:
            discard_tiles = []
        self._discard_tiles = discard_tiles
        self._player = player

    def is_key_event(self, event):
        return self._player.is_discard(event) or is_game_init(event)


class DoraIndicators(GameState):
    def scan(self, event) -> GameState:
        if is_game_init(event):
            seed_list = number_list(event.attrib["seed"])
            return DoraIndicators([seed_list[-1]])
        elif is_dora_indicator_event(event):
            return DoraIndicators(self._dora_indicators + [int(event.attrib['hai'])])
        else:
            return self

    def __init__(self, dora_indicators=None) -> None:
        super().__init__()
        if dora_indicators is None:
            dora_indicators = []
        self._dora_indicators = dora_indicators

    @property
    def value(self) -> List[int]:
        return self._dora_indicators

    def is_key_event(self, event):
        return is_game_init(event) or is_dora_indicator_event(event)


class InvisibleTiles(GameState):
    def __init__(self, player_num: int, invisible_tiles=None):
        if invisible_tiles is None:
            tile_total = len(TENHOU_TILE_CATEGORY)
            if player_num == 4:
                invisible_tiles = set(range(tile_total))
            elif player_num == 3:
                color_1m_9m = ((0, num, i) for num, i in product([1 - 1, 9 - 1], range(4)))
                others = range(TENHOU_TILE_CATEGORY.index((1, 0, 0)), tile_total)
                invisible_tiles = set(chain(color_1m_9m, others))
        self._invisible_tiles = invisible_tiles
        self._player_num = player_num

    def scan(self, event) -> GameState:
        if is_game_init(event):
            brand = InvisibleTiles(self._player_num)
            dora_indicator = DoraIndicators().scan(event).value
            brand._invisible_tiles -= set(dora_indicator)
            return brand

        discard_val = discard_value(event)
        if discard_val:
            return InvisibleTiles(self._player_num, self._invisible_tiles - {discard_val})
        elif is_open_hand(event):
            return InvisibleTiles(self._player_num, self._invisible_tiles - set(meld_from(event).self_tiles))
        elif is_dora_indicator_event(event):
            return InvisibleTiles(self._player_num, self._invisible_tiles - set(DoraIndicators().scan(event).value))
        return self

    @property
    def value(self) -> Set[int]:
        return self._invisible_tiles
