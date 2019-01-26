from __future__ import annotations

from abc import ABCMeta, abstractmethod
from argparse import Namespace
from typing import List

from .reader import TenhouPlayer, number_list, tile_from_tenhou
from .util import meld_from, TenhouMeld, TenhouAddedKan, Meld, Triplet, KanFromTriplet


class GameState(metaclass=ABCMeta):
    @abstractmethod
    def scan(self, event) -> GameState:
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def is_key_event(self, event) -> bool:
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


def is_game_init(event):
    return event.tag == "INIT"


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

    def is_key_event(self, event):
        player = self._player
        return is_game_init(event) \
               or player.is_discard(event) \
               or player.is_draw(event) \
               or player.is_open_hand(event)


def is_triplet_of(item: Triplet, added: TenhouAddedKan):
    added_tile = tile_from_tenhou(list(added.self_tiles)[0])
    triplet_representative = tile_from_tenhou(list(item.self_tiles)[0])
    return added_tile == triplet_representative


class PlayerMeld(GameState):
    def __init__(self, player: TenhouPlayer, meld_list=None) -> None:
        super().__init__()
        if meld_list is None:
            meld_list = []

        self._meld_list: List[Meld] = meld_list
        self._player = player

    def scan(self, event) -> GameState:
        if self.is_key_event(event):
            meld = meld_from(event)
            if isinstance(meld, TenhouAddedKan):
                return PlayerMeld(self._player,
                                  [(KanFromTriplet(item, meld)
                                    if isinstance(item, Triplet) and is_triplet_of(item, meld)
                                    else item)
                                   for item in self._meld_list]
                                  )
            else:
                return PlayerMeld(self._player, self._meld_list + [meld])
        return self

    @property
    def value(self):
        return self._meld_list

    def is_key_event(self, event):
        return self._player.is_open_hand(event)


class DiscardTiles(GameState):
    def scan(self, event) -> GameState:
        if self.is_key_event(event):
            return DiscardTiles(self._player, self._discard_tiles + [self._player.discard_tile_index(event)])
        return self

    @property
    def value(self):
        return self._discard_tiles

    def __init__(self, player: TenhouPlayer, discard_tiles=None):
        if discard_tiles is None:
            discard_tiles = []
        self._discard_tiles = discard_tiles
        self._player = player

    def is_key_event(self, event):
        return self._player.is_discard(event)


def is_dora_indicator_event(event):
    return event.tag == "DORA"


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
    def value(self):
        return self._dora_indicators

    def is_key_event(self, event):
        return is_game_init(event) or is_dora_indicator_event(event)
