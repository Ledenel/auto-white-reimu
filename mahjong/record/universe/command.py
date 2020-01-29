import ast
from collections import namedtuple
from typing import List, TypeVar, Callable, Iterable

from loguru import logger

from mahjong.record.universe.format import View, Update


def assertion(func):
    def _check_assert(x):
        try:
            func(x)
            return True
        except AssertionError:
            return False

    return _check_assert


class PropertyTypeManager:
    def __init__(self):
        self._checker = {}
        self._default_value = {}

    def get_default(self, view: View):
        view_typ = view.type
        for typ, default_ctor in self._default_value.items():
            if view_typ in typ:
                return default_ctor()

    def assertion_check(self, name):
        def _assertion_wrapper(func):
            checker = assertion(func)
            self._checker[name] = checker
            return checker

        return _assertion_wrapper

    def register_default_ctor(self, name):
        def _default_value_wrapper(func):
            self._default_value[name] = func

        return _default_value_wrapper


def is_empty(x):
    return x is None or x != x


def norm_empty(x):
    return None if is_empty(x) else x


def norm_value_str(x: str):  # FIXME: take caution about type with str
    return ast.literal_eval(x) if x != "" else None


class GameProperty:
    def __init__(self, view_property: View, update_method: Update):
        self.view_property = view_property
        self.update_method = update_method
        # self.default_ctor = default_ctor

    @property
    def scope(self):
        return self.view_property.scope


_Game_command = namedtuple(
    "GameCommand_",
    field_names=[
        "timestamp",
        "scope",
        "sub_scope_id",
        "property",
        "update_method",
        "value",
    ]
)


class GameCommand:
    def __init__(self, *, prop: View, update: Update, sub_scope=None, value=None, timestamp=None):
        self.timestamp = timestamp
        # if value is None and prop.default_ctor is not None and prop.update_method != Update.CLEAR:
        #     self.value = prop.default_ctor()
        # else:
        self.sub_scope_id = sub_scope
        self.value = value
        self.property = prop
        self.update_method = update
        self.prop = GameProperty(self.property, self.update_method)

    # @staticmethod
    # def multi_command(props: Iterable[GameProperty], sub_scope_id=None, value=None, timestamp=None):
    #     return [GameCommand(
    #         prop,
    #         sub_scope_id=sub_scope_id,
    #         value=value,
    #         timestamp=timestamp
    #     ) for prop in props]

    def __str__(self):
        return str(self.to_record())

    def __repr__(self):
        return "{%s}" % str(self)

    def to_record(self):
        return _Game_command(
            timestamp=self.timestamp,
            scope=self.prop.scope.name,
            sub_scope_id=self.sub_scope_id,
            property=self.prop.view_property.name,
            update_method=self.prop.update_method.name,
            value=self.value,
        )

    @staticmethod
    def from_record(record: _Game_command):
        return GameCommand(
            prop=View.by_name(record.scope)[record.property],
            update=Update[record.update_method],
            sub_scope=norm_empty(record.sub_scope_id),
            value=norm_empty(record.value),
            timestamp=norm_empty(record.timestamp),
        )


EventT = TypeVar('EventT')
EventTransform = Callable[[EventT], Iterable[GameCommand]]


class CommandTranslator:
    def __init__(self):
        self.defaults = []
        self.defaults: List[EventTransform]

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

    def postprocess(self, command: List[GameCommand]) -> List[GameCommand]:
        return command

    def translate(self, event: EventT) -> List[GameCommand]:
        pass

    def __call__(self, event: EventT) -> List[GameCommand]:
        event = self.preprocess(event)
        return_value = self.translate(event)
        if return_value:
            return return_value
        return_value = CommandTranslator.fallback_call(event, self.defaults)
        if return_value:
            return_value = self.postprocess(return_value)
            return return_value
        else:
            logger.warning("event <{}> is not transformed to game commands.", event)
            return []
