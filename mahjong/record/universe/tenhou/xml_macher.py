from collections import defaultdict
from xml.etree.ElementTree import Element

from typing import List, Callable, Optional

from loguru import logger

from mahjong.record.universe.format import GameCommand
from mahjong.record.utils.event import TenhouEvent

EventTransform = Callable[[TenhouEvent], List[GameCommand]]


class TenhouEventMatcher:
    def __init__(self):
        self.name_match = defaultdict(list)
        self.attr_match = defaultdict(list)
        self.both_match = defaultdict(list)
        self.defaults = []
        self.defaults: List[EventTransform]

    @staticmethod
    def fallback_call(event, matchers: List[EventTransform]) -> List[GameCommand]:
        for matcher in matchers:
            value = matcher(event)
            if value:
                return value

    def __call__(self, event: TenhouEvent) -> List[GameCommand]:
        name = event.tag
        for attr in event.attrib:
            both_key = (name, attr)
            if both_key in self.both_match:
                return_value = TenhouEventMatcher.fallback_call(
                    event,
                    self.both_match[both_key]
                )
                if return_value:
                    return return_value

        if name in self.name_match:
            return_value = TenhouEventMatcher.fallback_call(
                event,
                self.name_match[name]
            )
            if return_value:
                return return_value

        for attr in event.attrib:
            if attr in self.attr_match:
                return_value = TenhouEventMatcher.fallback_call(
                    event,
                    self.attr_match[attr]
                )
                if return_value:
                    return return_value

        return_value = TenhouEventMatcher.fallback_call(event, self.defaults)
        if return_value:
            return return_value
        else:
            logger.warning("event {} is not transformed to game commands.", event)
            return []


_global_matcher = TenhouEventMatcher()


def to_commands(event: TenhouEvent) -> List[GameCommand]:
    return _global_matcher(event)


def match_name(name: str) -> Callable[[EventTransform], EventTransform]:
    def _matcher_decor(func: EventTransform):
        _global_matcher.name_match[name].append(func)
        return func

    return _matcher_decor


def match_attr(name: str) -> Callable[[EventTransform], EventTransform]:
    def _matcher_decor(func: EventTransform):
        _global_matcher.attr_match[name].append(func)
        return func

    return _matcher_decor


def match_both(*, name: str, attr=str) -> Callable[[EventTransform], EventTransform]:
    def _matcher_decor(func: EventTransform):
        _global_matcher.both_match[(attr, name)].append(func)
        return func

    return _matcher_decor


def default_event(func: EventTransform) -> EventTransform:
    _global_matcher.defaults.append(func)
    return func
