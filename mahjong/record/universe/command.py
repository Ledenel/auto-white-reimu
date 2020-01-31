import ast
from collections import namedtuple
from typing import List, TypeVar, Callable, Iterable

import numpy
import pandas
from loguru import logger

from mahjong.record.universe.property_manager import prop_manager
from mahjong.record.universe.format import View, Update


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


command_field_names = [
    "timestamp",
    "scope",
    "sub_scope_id",
    "property",
    "update_method",
    "value",
]

_Game_command = namedtuple(
    "GameCommand_",
    field_names=command_field_names
)

command_field_names_set = set(command_field_names)


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
        return str(self.to_raw_record())

    def __repr__(self):
        return "{%s}" % str(self)

    @staticmethod
    def clean(pandas_dataframe):
        return pandas_dataframe.apply(GameCommand.pandas_columns_clean, axis="columns")

    @staticmethod
    def to_dataframe(command_list, raw=False):
        if raw:
            return pandas.DataFrame(
                (x.to_raw_record() for x in command_list),
            )
        else:
            return pandas.DataFrame(
                (x.to_record() for x in command_list),
            )

    @staticmethod
    def read_clean_csv(csv_path):
        return GameCommand.clean(pandas.read_csv(csv_path))

    @staticmethod
    def pandas_columns_clean(row):
        # remove index
        row = row[command_field_names]
        series_ctor = type(row)
        record = _Game_command(**row)
        command = GameCommand.from_record(record)
        target = numpy.array(command.to_raw_record(), dtype=object)
        target_series = series_ctor(target)
        target_series.index = command_field_names
        return target_series

    def to_raw_record(self):
        return _Game_command(
            timestamp=self.timestamp,
            scope=self.prop.scope,
            sub_scope_id=self.sub_scope_id,
            property=self.prop.view_property,
            update_method=self.prop.update_method,
            value=self.value,
        )

    @staticmethod
    def from_raw_record(record: _Game_command):
        return GameCommand(
            prop=record.property,
            update=record.update_method,
            sub_scope=norm_empty(record.sub_scope_id),
            value=norm_empty(record.value),
            timestamp=norm_empty(record.timestamp),
        )

    def to_record(self):
        return _Game_command(
            timestamp=self.timestamp,
            scope=self.prop.scope.name,
            sub_scope_id=self.sub_scope_id,
            property=self.prop.view_property.name,
            update_method=self.prop.update_method.name,
            value=prop_manager.to_str(self.value, prop=self.prop.view_property),
        )

    @staticmethod
    def from_record(record: _Game_command):
        view = View.by_name(record.scope)[record.property]
        return GameCommand(
            prop=view,
            update=Update[record.update_method],
            sub_scope=norm_empty(record.sub_scope_id),
            value=prop_manager.from_str(record.value, prop=view),
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

    def postprocess(self, event: EventT, command: List[GameCommand]) -> List[GameCommand]:
        return command

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
