import ast
from collections import namedtuple

import numpy
import pandas

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
    "state"
]

_Game_command = namedtuple(
    "GameCommand_",
    field_names=command_field_names
)

command_field_names_set = set(command_field_names)


class GameCommand:
    def __init__(self, *, prop: View, update: Update, sub_scope=None, value=None, timestamp=None, state=None):
        self.timestamp = timestamp
        # if value is None and prop.default_ctor is not None and prop.update_method != Update.CLEAR:
        #     self.value = prop.default_ctor()
        # else:
        self.sub_scope_id = sub_scope
        self.value = value
        self.property = prop
        self.update_method = update
        self.state = state
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
            state=self.state,
        )

    @staticmethod
    def from_raw_record(record: _Game_command):
        return GameCommand(
            prop=record.property,
            update=record.update_method,
            sub_scope=norm_empty(record.sub_scope_id),
            value=norm_empty(record.value),
            timestamp=norm_empty(record.timestamp),
            state=norm_empty(record.state),
        )

    def to_record(self):
        return _Game_command(
            timestamp=self.timestamp,
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
            update=Update[record.update_method],
            sub_scope=norm_empty(record.sub_scope_id),
            value=prop_manager.from_str(record.value, prop=view),
            timestamp=norm_empty(record.timestamp),
            state=prop_manager.from_str(record.state, prop=view),
        )


