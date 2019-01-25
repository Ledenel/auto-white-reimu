from __future__ import annotations

from abc import ABCMeta, abstractmethod
from argparse import Namespace
from typing import List

from record.reader import TenhouPlayer, number_list, tile_from_tenhou
from record.util import meld_from, TenhouMeld, TenhouAddedKan, Meld, Triplet, KanFromTriplet


class GameState(metaclass=ABCMeta):
    @abstractmethod
    def scan(self, event) -> GameState:
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    @property
    @abstractmethod
    def is_key_event(self):
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
    @property
    def is_key_event(self):
        return self._composed_key_event_func

    def __init__(self, **states):
        super().__init__()
        self._states = states
        self._name_space_state = Namespace(**states)

        def is_composed_key_event(event):
            return any(st.is_key_event(event) for st in states.values())

        self._composed_key_event_func = is_composed_key_event

    @property
    def value(self):
        return self._name_space_state

    def scan(self, event) -> GameState:
        return GameStateCollection(
            **{k: v.scan(event) for k, v in self._states.items()}
        )


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

        def hand_is_key_event(event):
            return event.tag == "INIT" \
                   or player.is_discard(event) \
                   or player.is_draw(event) \
                   or player.is_open_hand(event)

        self._key_event_func = hand_is_key_event

    def scan(self, event) -> GameState:
        if event.tag == "INIT":
            return PlayerHand(self._player, set(number_list(event.attrib['hai%d' % self._player.index])))
        elif self._player.is_draw(event):
            return PlayerHand(self._player, self.hand | {self._player.draw_tile_index(event)})
        elif self._player.is_discard(event):
            return PlayerHand(self._player, self.hand - {self._player.discard_tile_index(event)})
        elif self._player.is_open_hand(event):
            meld = meld_from(event)
            return PlayerHand(self._player, self.hand - meld.self_tiles)
        return self

    @property
    def is_key_event(self):
        return self._key_event_func


def is_triplet_of(item: Triplet, added: TenhouAddedKan):
    added_tile = tile_from_tenhou(list(item.self_tiles)[0])
    triplet_representative = tile_from_tenhou(list(item.self_tiles)[0])
    return added_tile == triplet_representative


class PlayerMeld(GameState):
    def __init__(self, player: TenhouPlayer, meld_list=None) -> None:
        super().__init__()
        if meld_list is None:
            meld_list = []

        def meld_key(event):
            return self._player.is_open_hand(event)

        self._meld_list: List[Meld] = meld_list
        self._player = player
        self._meld_key = meld_key

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

    @property
    def is_key_event(self):
        return self._meld_key
