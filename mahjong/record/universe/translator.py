from typing import TypeVar, Callable, Iterable, List, Mapping

from loguru import logger

from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.interpreter import GameInterpreter

EventT = TypeVar('EventT')
EventTransform = Callable[[EventT, Mapping], Iterable[GameCommand]]


class CommandTranslator:
    def __init__(self):
        self.defaults = []
        self.defaults: List[EventTransform]
        self.interpreter = GameInterpreter()

    @staticmethod
    def fallback_call(event, matchers: List[EventTransform]) -> List[GameCommand]:
        for matcher in matchers:
            value = list(matcher(event))
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

    def __call__(self, event: EventT, strict=False) -> List[GameCommand]:
        event = self.preprocess(event)
        return_value = self.translate(event)
        if return_value:
            return self.postprocess(event, return_value)
        return_value = CommandTranslator.fallback_call(event, self.defaults)
        if return_value:
            return self.postprocess(event, return_value)
        else:
            if strict:
                raise ValueError("event <{}> is not transformed to game commands.".format(event))
            else:
                logger.warning("event <{}> is not transformed to game commands.", event)
            return []