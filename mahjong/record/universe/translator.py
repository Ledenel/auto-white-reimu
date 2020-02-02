from typing import TypeVar, Callable, Iterable, List, Mapping

from loguru import logger

from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.format import EventType
from mahjong.record.universe.interpreter import GameInterpreter

EventT = TypeVar('EventT')
EventTransform = Callable[[EventT, Mapping], Iterable[GameCommand]]


def default_event_type(typ: EventType):
    def _event_type_decor(func: EventTransform):
        def _modify_event_type(event, ctx):
            for cmd in func(event, ctx):
                if cmd.event is None:
                    cmd.event = typ
                yield cmd

        return _modify_event_type

    return _event_type_decor


class CommandTranslator:
    def __init__(self):
        self.defaults = []
        self.defaults: List[EventTransform]
        self.interpreter = GameInterpreter()

    def fallback_call(self, event, matchers: List[EventTransform]) -> List[GameCommand]:
        for matcher in matchers:
            value = list(matcher(event, self.interpreter.state))
            if value:
                return value

    # TODO: add preprocess and postprocess for event and command list. (to support timestamp attaching in tenhou).

    def default_event(self, func: EventTransform) -> EventTransform:
        self.defaults.append(func)
        return func

    def preprocess(self, event: EventT) -> EventT:
        return event

    def postprocess(self, event: EventT, commands: List[GameCommand]) -> List[GameCommand]:
        for cmd in commands:
            cmd.state = self.interpreter.interpret(cmd)
        return commands

    def translate(self, event: EventT) -> List[GameCommand]:
        pass

    def clear(self):
        self.interpreter.state = {}

    def __call__(self, event: EventT, strict=False) -> List[GameCommand]:
        event = self.preprocess(event)
        return_value = self.translate(event)
        if return_value:
            return self.postprocess(event, return_value)
        return_value = self.fallback_call(event, self.defaults)
        if return_value:
            return self.postprocess(event, return_value)
        else:
            if strict:
                raise ValueError("event <{}> is not transformed to game commands.".format(event))
            else:
                logger.warning("event <{}> is not transformed to game commands.", event)
            return []
