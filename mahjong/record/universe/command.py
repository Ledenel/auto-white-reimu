import ast
from collections import namedtuple

import numpy
import pandas

from mahjong.record.universe.property_manager import prop_manager
from mahjong.record.universe.format import View, Update, EventType


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
    "event",
    "scope",
    "sub_scope_id",
    "property",
    "update_method",
    "value",
    "state"
]

_Game_command = namedtuple(
    "GameCommand_",
    field_names=command_field_names
)

command_field_names_set = set(command_field_names)

def try_int(x):
    if isinstance(x, str) and x.isdigit():
        return int(x)
    return x

class GameCommand:
    def __init__(self, *, prop: View, update: Update, sub_scope="all", value=None, timestamp=None, state=None, event=None):
        self.event = event
        self.timestamp = timestamp
        self.sub_scope_id = sub_scope
        self.value = value
        self.property = prop
        self.update_method = update
        self.state = state
        self.prop = GameProperty(self.property, self.update_method)

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
    def pandas_columns_clean(row_origin):
        # remove index
        row = row_origin[command_field_names]
        record = _Game_command(**row)
        command = GameCommand.from_record(record)
        row_return = row_origin.copy()
        for name, value in command.to_raw_record()._asdict().items():
            row_return[name] = value
        return row_return

    def to_raw_record(self):
        return _Game_command(
            timestamp=self.timestamp,
            event=self.event,
            scope=self.prop.scope,
            sub_scope_id=self.sub_scope_id,
            property=self.prop.view_property,
            update_method=self.prop.update_method,
            value=self.value,
            state=self.state,
        )

    @staticmethod
    def from_raw_record(record: _Game_command):
        return GameCommand(
            prop=record.property,
            event=record.event,
            update=record.update_method,
            sub_scope=try_int(record.sub_scope_id),
            value=norm_empty(record.value),
            timestamp=norm_empty(record.timestamp),
            state=norm_empty(record.state),
        )

    def to_record(self):
        return _Game_command(
            timestamp=self.timestamp,
            event=self.event.name if self.event is not None else None,
            scope=self.prop.scope.name,
            sub_scope_id=self.sub_scope_id,
            property=self.prop.view_property.name,
            update_method=self.prop.update_method.name,
            value=prop_manager.to_str(self.value, prop=self.prop.view_property),
            state=prop_manager.to_str(self.state, prop=self.prop.view_property),
        )

    @staticmethod
    def from_record(record: _Game_command):
        view = View.by_name(record.scope)[record.property]
        return GameCommand(
            prop=view,
            event=None if is_empty(record.event) else EventType[record.event],
            update=Update[record.update_method],
            sub_scope=try_int(record.sub_scope_id),
            value=prop_manager.from_str(record.value, prop=view),
            timestamp=norm_empty(record.timestamp),
            state=prop_manager.from_str(record.state, prop=view),
        )
