import operator

from typing import Iterable

from loguru import logger

from mahjong.record.universe.command import GameCommand
from mahjong.record.universe.interpreter import execute_new_value
from mahjong.record.universe.property_manager import prop_manager
from mahjong.record.universe.format import *
import mahjong.record.universe.format as mahjong_format
import pandas as pd


def get_enums_from(module):
    for name in dir(module):
        typ = getattr(module, name)
        if isinstance(typ, type) and issubclass(typ, Enum):
            yield name, typ


enums = dict(get_enums_from(mahjong_format))


def replace_enum_values(value_str):
    if isinstance(value_str, str):
        split = value_str.split(".")
        if len(split) == 2:
            typ, name = split
            return enums[typ][name]
    return value_str


def null():
    return None


defaultExecutor = {
    Update.RESET_DEFAULT: null,
    Update.ADD: operator.add,
    Update.REMOVE: operator.sub,
}


def fill_value_executor():
    return {
        Update.ADD: operator.add,
        Update.REMOVE: operator.sub,
    }


def remove_all(lst: list, values: list):
    lst_r = lst.copy()
    for val in values:
        lst_r.remove(val)
    return lst_r


listExecutor = {
    Update.ADD: operator.add,
    Update.REMOVE: remove_all,
}

setExecutor = {
    Update.ADD: operator.or_,
    Update.REMOVE: operator.sub,
}


# def setdefault(self, k, default):
#     if k in self:
#         return self
#     self
class CombinedCommandExecutor:
    def __init__(self, executor_with_type):
        self.executor_with_type = executor_with_type

    def has_function(self, value, method: Update):
        for typ, executor in self.executor_with_type:
            if typ is None or isinstance(value, typ):
                if method in executor:
                    return True
        return False

    def execute_value(self, command: GameCommand, origin_value=None):
        for typ, executor in self.executor_with_type:
            if typ is None or isinstance(command.value, typ):
                method = command.prop.update_method
                if method.operand_num() == 2:
                    return executor[method](origin_value, command.value)
                elif method.operand_num() == 1:
                    return executor[method](command.value)
                elif method.operand_num() == 0:
                    raise ValueError("Zero operand is not supported. Type of None value may be ambiguous.")


def state_series_apply(x):
    col_last = x.name[-1]
    if hasattr(col_last, "type"):
        def from_str_view(t):
            return prop_manager.from_str(t, col_last)

        return x.apply(from_str_view)
    return x



class GameExecutor:
    @staticmethod
    def read_clean_csv(csv_path):
        df_states = pd.read_csv(csv_path, header=[0, 1, 2], skipinitialspace=True)
        df_states = df_states.rename(columns=replace_enum_values)
        df_states = df_states.apply(state_series_apply, axis="rows")
        return df_states

    def __init__(self, strict_mode=False):
        self.strict_mode = strict_mode
        self.executor = CombinedCommandExecutor([
            (list, listExecutor),
            (set, setExecutor),
            (None, defaultExecutor),
        ])
        state_dict = {
            enum: {
                "single": {},
            } if multi_value is None else {
                key: {} for key in multi_value
            } for enum, multi_value in ViewScope.scopes_with_multi_value().items()
        }
        all_dict = {
            "global": {
                "time": {

                },
            },
            **state_dict
        }
        self.states = TransferDict(all_dict)

    @staticmethod
    def state_value(state_dict, command: GameCommand):
        scope_key = command.prop.scope
        multi_values = ViewScope.scopes_with_multi_value()[scope_key]
        if multi_values is None:
            return state_dict[scope_key]["single"]
        else:
            return state_dict[scope_key][multi_values(command.sub_scope_id)]

    def execute(self, commands: Iterable[GameCommand]):
        curr_state = self.states
        for command in commands:
            curr_state = self.execute_update_state(command, curr_state)
            yield curr_state["global"]["time"].set("timestamp", command.timestamp)

    def execute_as_dataframe(self, commands: Iterable[GameCommand]):
        df = pd.DataFrame(x.flatten() for x in self.execute(commands))
        df.columns = pd.MultiIndex.from_tuples(df.columns)
        return df

    def execute_update_state(self, command, curr_state):
        view = GameExecutor.state_value(curr_state, command)
        old_value = view.get(command.prop.view_property, None)
        new_value, view_property = execute_new_value(self.executor, command, old_value)

        if command.prop.update_method == Update.ASSERT_EQUAL_OR_SET:
            expected = new_value
            if view_property in view:
                actual = old_value
                is_equal = prop_manager.equal_value(expected, actual, view=view_property)
                msg = "{} != {} when executing {cmd}".format(expected, actual, cmd=command)
                if self.strict_mode:
                    assert is_equal, msg
                elif not is_equal:
                    logger.warning(msg)

        result_state = view.set(
            view_property,
            new_value,
        )
        return result_state


class TransferDict:
    def __init__(self, nested_dict, parent=None, parent_key=None):
        self.parent: TransferDict = parent
        self.parent_key = parent_key
        self.nested_dict = {
            k: self.transfer_value(k, v)  # fix construction (also copy TransferDict)
            for k, v in nested_dict.items()
        }

    def flatten_iter(self):
        for k, v in self.nested_dict.items():
            initial = [k]
            if isinstance(v, TransferDict):
                for sub_k, sub_v in v.flatten_iter():
                    yield tuple(initial + list(sub_k)), sub_v
            else:
                yield tuple(initial), v

    def flatten(self):
        return dict((k, prop_manager.to_str(v, k[-1])) for k, v in self.flatten_iter())

    def __getattr__(self, item):
        return getattr(self.nested_dict, item)

    def __getitem__(self, item):
        return self.nested_dict[item]

    def __contains__(self, item):
        return item in self.nested_dict

    def __str__(self):
        return str(self.nested_dict)

    def __repr__(self):
        return repr(self.nested_dict)

    def _readonly(self, *args, **kwards):
        raise NotImplemented

    __setitem__ = __delattr__ = pop = update = popitem = _readonly

    def set(self, key, value):
        modified_dict = {
            **self.nested_dict,
            key: value
        }
        modified = TransferDict(modified_dict, parent=self.parent, parent_key=self.parent_key)
        if self.parent is not None:
            return self.parent.set(
                self.parent_key, modified
            )
        else:
            # modified._update_link()
            return modified

    # def _update_link(self):
    #     for k,v in self.nested_dict.items():
    #         if isinstance(v, TransferDict):
    #             v.parent = self
    #             v.parent_key =

    def drop(self, key):
        dict_cpy = self.nested_dict.copy()
        del dict_cpy[key]
        modified = TransferDict(dict_cpy)
        return self.parent.set(
            self.parent_key, modified
        ) if self.parent is not None else modified

    def setdefault(self, key, default):
        if key not in self:
            return self.set(key, default)
        else:
            return self

    def transfer_value(self, k, v):
        if isinstance(v, dict):
            return TransferDict(v, self, k)
        elif isinstance(v, TransferDict):
            return TransferDict(v.nested_dict, self, k)
        else:
            return v
