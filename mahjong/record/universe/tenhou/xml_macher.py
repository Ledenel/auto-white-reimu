from collections import defaultdict

from typing import List, Callable

from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.translator import EventTransform, CommandTranslator
from mahjong.record.utils.event import TenhouEvent


class TenhouCommandTranslator(CommandTranslator):
    def __init__(self):
        super().__init__()
        self.name_match = defaultdict(list)
        self.attr_match = defaultdict(list)
        self.both_match = defaultdict(list)

    def match_name(self, name: str) -> Callable[[EventTransform], EventTransform]:
        def _matcher_decor(func: EventTransform):
            self.name_match[name].append(func)
            return func

        return _matcher_decor

    def match_names(self, names: List[str]) -> Callable[[EventTransform], EventTransform]:
        def _matcher_decor(func: EventTransform):
            for name in names:
                self.name_match[name].append(func)
            return func

        return _matcher_decor

    def postprocess(self, event: TenhouEvent, commands: List[GameCommand]) -> List[GameCommand]:
        super().postprocess(event, commands)
        for cmd in commands:
            cmd.timestamp = event.timestamp
        return commands

    def match_attr(self, name: str) -> Callable[[EventTransform], EventTransform]:
        def _matcher_decor(func: EventTransform):
            self.attr_match[name].append(func)
            return func

        return _matcher_decor

    def match_both(self, *, name: str, attr: str) -> Callable[[EventTransform], EventTransform]:
        def _matcher_decor(func: EventTransform):
            self.both_match[(attr, name)].append(func)
            return func

        return _matcher_decor

    def translate(self, event: TenhouEvent) -> List[GameCommand]:
        name = event.tag
        for attr in event.attrib:
            both_key = (name, attr)
            if both_key in self.both_match:
                return_value = CommandTranslator.fallback_call(
                    event,
                    self.both_match[both_key]
                )
                if return_value:
                    return return_value

        if name in self.name_match:
            return_value = CommandTranslator.fallback_call(
                event,
                self.name_match[name]
            )
            if return_value:
                return return_value

        for attr in event.attrib:
            if attr in self.attr_match:
                return_value = CommandTranslator.fallback_call(
                    event,
                    self.attr_match[attr]
                )
                if return_value:
                    return return_value


tenhou_command = TenhouCommandTranslator()
